from django.contrib import admin
from accounts.models import UserWallet, Transaction


admin.site.register(UserWallet)
admin.site.register(Transaction)
