from django.contrib import admin

from .models import Account, SalesInvoice
admin.site.register(Account)
admin.site.register(SalesInvoice)