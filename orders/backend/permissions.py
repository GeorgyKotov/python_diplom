from rest_framework import permissions

class IsAuthenticatedClient(permissions.IsAuthenticated):
    """
    Базовое разрешение — аутентифицированный пользователь.
    Дополнительно можно требовать is_supplier=False, если нужно разграничение.
    """
    def has_permission(self, request, view):
        ok = super().has_permission(request, view)
        if not ok:
            return False
        # допускаем всех аутентифицированных как клиентов; если пользователю нужен строгий check,
        # можно проверять request.user.profile.is_supplier == False
        return True


class IsSupplier(permissions.IsAuthenticated):
    """
    Проверяем, что у пользователя есть профиль поставщика (profile.is_supplier=True).
    Требует, чтобы у пользователя был атрибут profile.
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        profile = getattr(request.user, 'profile', None)
        return bool(profile and getattr(profile, 'is_supplier', False))