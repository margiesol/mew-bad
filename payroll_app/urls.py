from django.urls import path

from django.contrib import admin
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_redirect, name="home"),
    path('signup/', views.signup_view, name='signup'),
    path('manage_account/<int:pk>', views.manage_account, name='manage_account'),
    path('delete_account/<int:pk>', views.delete_account, name='delete_account'),
    path('change_password/<int:pk>', views.change_password, name='change_password'),
    path('main_page/', views.main_page, name='main_page'),

    path('profiles/', views.profiles, name='profiles'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/update/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('customer/create/', views.customer_create, name='customer_create'),
    path('customer/<int:pk>/update/', views.customer_update, name='customer_update'),
    path('customer/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    #path('supplier/create/', views.supplier_create, name='supplier_create'),
    #path('supplier/<int:pk>/update/', views.supplier_update, name='supplier_update'),
    #path('supplier/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    path('create_invoice/', views.create_invoice, name='create_invoice'),
    path('sales_invoice/create/', views.sales_invoice_create, name='sales_invoice_create'),
    path('sales_invoice/<int:invoice_id>/print/', views.sales_invoice_print, name='sales_invoice_print'),
    path('purchase_invoice/create/', views.purchase_invoice_create, name='purchase_invoice_create'),
    path('purchase_invoice/<int:pk>/print/', views.purchase_invoice_print, name='purchase_invoice_print'),
]