import json
import yaml
import openpyxl
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status

from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from .permissions import IsSupplier


class SimpleProductImportView(APIView):
    """
    - Поддерживает 3 формата: YAML, JSON, Excel (.xlsx)
    """

    # Разрешаем загружать файлы формата multipart/form-data
    parser_classes = (MultiPartParser,)

    # Только поставщик может загружать товары
    permission_classes = (IsSupplier,)

    def post(self, request):
        """
        Основной метод импорта.
        1. Получаем файл из запроса
        2. Определяем его формат по расширению
        3. Читаем данные и превращаем в python dict
        4. Создаём или обновляем записи в БД
        """

        # Пытаемся получить файл из запроса
        file = request.FILES.get('file')
        if not file:
            # Если файл не передан — возвращаем ошибку
            return Response({"error": "Файл не передан"}, status=status.HTTP_400_BAD_REQUEST)

        # Приводим имя файла к нижнему регистру, чтобы проще было сравнивать расширение
        name = file.name.lower()

        # Определяем, как парсить файл по его расширению
        if name.endswith(".yaml") or name.endswith(".yml"):
            # YAML можно загрузить сразу через safe_load
            data = yaml.safe_load(file.read())
        elif name.endswith(".json"):
            # JSON сначала читаем как текст, затем преобразуем через json.loads
            data = json.loads(file.read().decode('utf-8'))
        elif name.endswith(".xlsx"):
            # Для Excel вызываем отдельный метод
            data = self.parse_excel(file)
        else:
            # Если расширение не поддерживается — сообщаем об ошибке
            return Response({"error": "Формат файла не поддерживается"}, status=status.HTTP_400_BAD_REQUEST)

        # Определяем магазин, для которого выполняется импорт
        # Если в файле указано название магазина — берём его
        shop_name = data.get("shop", {}).get("name", "Unknown Shop")

        # Ищем магазин по имени, если нет — создаём
        shop, _ = Shop.objects.get_or_create(name=shop_name)

        # Получаем список товаров из данных
        products = data.get("products", [])

        # Счётчики для ответа ("простая статистика")
        created = 0
        updated = 0

        # Проходим по каждому товару из файла
        for item in products:
            # Название товара: если отсутствует, такой товар мы пропустим
            product_name = item.get("name")
            # Категория: если не указана, используем значение по умолчанию
            category_name = item.get("category", "Без категории")

            # Создаём или ищем категорию
            category, _ = Category.objects.get_or_create(name=category_name)

            # Создаём или ищем продукт (общую сущность, не привязанную к магазину)
            product, _ = Product.objects.get_or_create(name=product_name, category=category)

            # Создаём или ищем информацию о товаре в конкретном магазине (ProductInfo)
            # defaults — значения, которые будут установлены только если эта запись создаётся впервые
            pi, is_created = ProductInfo.objects.get_or_create(
                product=product,
                shop=shop,
                defaults={
                    "name": item.get("name_in_shop", product_name),
                    "quantity": item.get("quantity", 0),
                    "price": item.get("price", 0),
                    "price_rrc": item.get("price_rrc", 0),
                }
            )

            if is_created:
                # Если запись создана впервые — увеличиваем счётчик созданных
                created += 1
            else:
                # Если запись уже существовала — обновим её
                pi.name = item.get("name_in_shop", pi.name)
                pi.quantity = item.get("quantity", pi.quantity)
                pi.price = item.get("price", pi.price)
                pi.price_rrc = item.get("price_rrc", pi.price_rrc)
                pi.save()
                updated += 1

            # Работа с параметрами товара
            # format:
            # parameters:
            #   color: "red"
            #   memory: "128GB"
            params = item.get("parameters", {})

            # Проходим по всем параметрам
            for key, val in params.items():
                # Создаём или находим параметр
                param, _ = Parameter.objects.get_or_create(name=key)

                # Создаём или находим значение параметра для конкретного товара
                pp, pp_created = ProductParameter.objects.get_or_create(
                    product_info=pi,
                    parameter=param,
                    defaults={"value": val}
                )

                # Если параметр уже существовал — обновляем его значение
                if not pp_created:
                    pp.value = val
                    pp.save()

        # Возвращаем простой ответ клиенту
        return Response({
            "created": created,
            "updated": updated
        }, status=status.HTTP_200_OK)

    def parse_excel(self, file):
        """
        Метод для чтения Excel (.xlsx) файла.
        """

        # Открываем Excel-файл
        wb = openpyxl.load_workbook(file)
        ws = wb.active

        # Получаем все строки в виде списка
        rows = list(ws.values)

        # Первая строка — заголовки колонок
        headers = rows[0]
        products = []

        # Обрабатываем каждую строку после заголовков
        for row in rows[1:]:
            item = {}

            # Превращаем строку Excel в словарь вида { "column_name": value }
            for h, v in zip(headers, row):
                if h:
                    item[h] = v

            # Приводим Excel-формат к ожидаемой структуре
            products.append({
                "name": item.get("name"),
                "category": item.get("category"),
                "name_in_shop": item.get("name_in_shop"),
                "quantity": item.get("quantity"),
                "price": item.get("price"),
                "price_rrc": item.get("price_rrc"),
                "parameters": {}  # параметры пока не обрабатываем глубоко
            })

        # Возвращаем структуру данных в том же виде, что YAML/JSON
        return {"products": products}
