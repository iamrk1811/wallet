from rest_framework.permissions import BasePermission
from accounts.models import UserWallet

class WalletAccessPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            token = request.META['HTTP_AUTHORIZATION'].replace("Token ", "")
            user_wallet = UserWallet.objects.get(token=token)
            request.user_wallet = user_wallet
            return True
        except Exception:
            return False