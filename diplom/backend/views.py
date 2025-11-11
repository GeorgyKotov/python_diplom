import json
import yaml
import openpyxl
from rest_framework.parsers import MultiPartParser
from .models import Shop, Category, Product, Parameter, ProductParameter
from .permissions import IsSupplier
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import ProductInfo, Contact, Order, OrderItem
from .serializers import RegisterSerializer, LoginSerializer, ProductInfoSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Получаем модель пользователя (стандартная или кастомная, если указана в settings)
User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
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


# Вспомогательная функция для безопасного чтения данных из запроса (на случай, если JSON некорректный)
def _json_from_request(request):
    try:
        # В DRF request.data уже содержит распарсенный JSON
        return request.data if hasattr(request, 'data') else json.loads(request.body.decode() or '{}')
    except Exception:
        return {}


# Регистрация и Авторизация
@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(APIView):
    """
    POST /register
    Регистрирует нового пользователя.
    Создаём пользователя как неактивного, отправляем ему письмо со ссылкой для подтверждения.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        ser = RegisterSerializer(data=request.data)

        # Проверяем входные данные на заполненность
        if not ser.is_valid():
            return Response({"status": "ok", "detail": "Некорректные данные"}, status=status.HTTP_400_BAD_REQUEST)

        data = ser.validated_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        user.is_active = False  # Аккаунт станет активным после подтверждения email
        user.save()

        # Формируем ссылку для подтверждения регистрации
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = f"{request.scheme}://{request.get_host()}/confirm?uid={uid}&token={token}"

        # Отправляем письмо (в разработке уходит в консоль)
        send_mail(
            subject="Подтверждение регистрации",
            message=f"Для активации аккаунта перейдите по ссылке: {link}",
            from_email=None,
            recipient_list=[data['email']],
            fail_silently=True
        )

        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class ConfirmAPIView(APIView):
    """
    GET /confirm?uid=xxx&token=yyy
    Подтверждение регистрации по ссылке из письма.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')

        if not uid or not token:
            return Response({"status": "ok", "detail": "Отсутствуют параметры"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Декодируем uid и ищем пользователя
            uid_int = int(urlsafe_base64_decode(uid).decode())
            user = User.objects.get(pk=uid_int)
        except Exception:
            return Response({"status": "ok", "detail": "Некорректный uid"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем токен
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"status": "ok"})

        return Response({"status": "ok", "detail": "Некорректный token"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    """
    POST /login
    Авторизация пользователя. Создаём сессию при успешном входе.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        ser = LoginSerializer(data=request.data)

        if not ser.is_valid():
            return Response({"status": "ok", "detail": "Некорректные данные"}, status=status.HTTP_400_BAD_REQUEST)

        data = ser.validated_data
        user = authenticate(request, username=data['username'], password=data['password'])

        # Проверяем логин и пароль
        if user is None:
            return Response({"status": "ok", "detail": "Неверный логин или пароль"}, status=status.HTTP_401_UNAUTHORIZED)

        # Если пользователь не активирован — не пускаем
        if not user.is_active:
            return Response({"status": "ok", "detail": "Аккаунт не активирован"}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        return Response({"status": "ok"})


@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(APIView):
    """
    POST /logout
    Завершение сессии пользователя.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        logout(request)
        return Response({"status": "ok"})


# Каталог
@method_decorator(csrf_exempt, name='dispatch')
class CatalogAPIView(APIView):
    """
    GET /catalog
    Возвращает список доступных товаров (ProductInfo) с количеством > 0.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        products = ProductInfo.objects.filter(quantity__gt=0)
        ser = ProductInfoSerializer(products, many=True)
        return Response({"status": "ok", "items": ser.data})


# Корзина
@method_decorator(csrf_exempt, name='dispatch')
class CartAPIView(APIView):
    """
    Работа с корзиной.
    Корзина хранится в сессии (request.session).
    - GET: получить корзину
    - POST: добавить товар
    - DELETE: удалить товар
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Получаем корзину или пустую, если её ещё нет
        cart = request.session.get('cart', {})
        items = []

        # Собираем данные о товарах в корзине
        for pid, qty in cart.items():
            try:
                pi = ProductInfo.objects.get(pk=int(pid))
            except ProductInfo.DoesNotExist:
                continue

            items.append({
                "product_info": pi.pk,
                "product": str(pi.product),
                "shop": str(pi.shop),
                "price": float(pi.price),
                "quantity": qty
            })

        return Response({"status": "ok", "items": items})

    def post(self, request):
        data = _json_from_request(request)
        pid = data.get('product_info')
        qty = int(data.get('quantity', 1))

        if not pid:
            return Response({"status": "ok", "detail": "Нужно указать product_info"}, status=status.HTTP_400_BAD_REQUEST)

        cart = request.session.get('cart', {})
        cart[str(pid)] = cart.get(str(pid), 0) + qty
        request.session['cart'] = cart

        return Response({"status": "ok"})

    def delete(self, request):
        data = _json_from_request(request)
        pid = data.get('product_info')

        cart = request.session.get('cart', {})
        if str(pid) in cart:
            cart.pop(str(pid))
            request.session['cart'] = cart
            return Response({"status": "ok"})

        return Response({"status": "ok", "detail": "Товара нет в корзине"}, status=status.HTTP_404_NOT_FOUND)


# Контакты
@method_decorator(csrf_exempt, name='dispatch')
class ContactsAPIView(APIView):
    """
    Контакты пользователя (адреса/телефоны доставки).
    - GET: получить список
    - POST: создать новый
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        result = [{"id": c.pk, "type": c.type, "value": c.value} for c in contacts]
        return Response({"status": "ok", "contacts": result})

    def post(self, request):
        data = _json_from_request(request)
        contact_type = data.get('type', 'address')
        value = data.get('value')

        if not value:
            return Response({"status": "ok", "detail": "Не указано значение"}, status=status.HTTP_400_BAD_REQUEST)

        contact = Contact.objects.create(user=request.user, type=contact_type, value=value)
        return Response({"status": "ok", "id": contact.pk}, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class ContactDetailAPIView(APIView):
    """
    Работа с конкретным контактом по ID.
    - GET: получить контакт
    - DELETE: удалить
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        try:
            contact = Contact.objects.get(pk=pk, user=request.user)
        except Contact.DoesNotExist:
            return Response({"status": "ok", "detail": "Контакт не найден"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status": "ok", "id": contact.pk, "type": contact.type, "value": contact.value})

    def delete(self, request, pk):
        try:
            contact = Contact.objects.get(pk=pk, user=request.user)
        except Contact.DoesNotExist:
            return Response({"status": "ok", "detail": "Контакт не найден"}, status=status.HTTP_404_NOT_FOUND)

        contact.delete()
        return Response({"status": "ok"})


# Заказы
@method_decorator(csrf_exempt, name='dispatch')
class OrderCreateAPIView(APIView):
    """
    POST /diplom/create
    Создание заказа:
    - Если в корзине есть товары — берем оттуда
    - Если корзина пуста — можно передать товары в теле запроса
    После оформления заказа корзина очищается.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = _json_from_request(request)

        # Пытаемся взять товары из корзины (если пользователь добавлял ранее)
        cart = request.session.get('cart', {})
        items = []

        for pid, qty in cart.items():
            try:
                pi = ProductInfo.objects.get(pk=int(pid))
            except ProductInfo.DoesNotExist:
                continue

            items.append((pi, int(qty)))

        # Если корзина пустая — можно передать товары вручную в теле запроса
        if not items:
            body_items = data.get('items', [])
            for it in body_items:
                try:
                    pi = ProductInfo.objects.get(pk=int(it.get('product_info')))
                except ProductInfo.DoesNotExist:
                    continue

                items.append((pi, int(it.get('quantity', 1))))

        if not items:
            return Response({"status": "ok", "detail": "Нет товаров для заказа"}, status=status.HTTP_400_BAD_REQUEST)

        # Контакт обязателен — куда доставлять
        contact_id = data.get('contact_id')
        if not contact_id:
            return Response({"status": "ok", "detail": "Нужно указать contact_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contact = Contact.objects.get(pk=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response({"status": "ok", "detail": "Контакт не найден"}, status=status.HTTP_400_BAD_REQUEST)

        # Создаём заказ
        order = Order.objects.create(user=request.user, contact=contact)

        # Переносим товары из корзины в заказ
        for pi, qty in items:
            if pi.quantity >= qty:
                OrderItem.objects.create(order=order, product_info=pi, quantity=qty, price=pi.price)
                pi.quantity -= qty
                pi.save()

        # После оформления очищаем корзину
        if 'cart' in request.session:
            del request.session['cart']

        # Отправляем пользователю письмо с подтверждением (уходит в консоль в dev)
        send_mail(
            subject=f"Заказ №{order.pk} создан",
            message=f"Ваш заказ {order.pk} успешно оформлен.",
            from_email=None,
            recipient_list=[request.user.email],
            fail_silently=True
        )

        return Response({"status": "ok", "order_id": order.pk}, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class OrdersListAPIView(APIView):
    """
    GET /diplom
    Возвращает список заказов пользователя с товарами внутри.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-pk')
        result = []

        for order in orders:
            items = []
            for item in order.orderitem_set.all():
                items.append({
                    "product": str(item.product_info.product),
                    "shop": str(item.product_info.shop),
                    "qty": item.quantity,
                    "price": float(item.price)
                })

            result.append({
                "id": order.pk,
                "status": getattr(order, "status", "new"),  # Если статус есть — покажем, иначе 'new'
                "items": items
            })

        return Response({"status": "ok", "diplom": result})