from django.contrib import admin
from .models import Agent, Bank, Customer, Product

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Agent)
admin.site.register(Bank)
