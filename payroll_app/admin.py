from django.contrib import admin

from .models import Account, SalesTransaction
admin.site.register(Account)
admin.site.register(SalesTransaction)