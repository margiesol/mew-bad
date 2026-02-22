from django.urls import path
from . import views

urlpatterns = [
    # Home / main
    path("", views.home_redirect, name="home_redirect"),
    path("main/", views.main_page, name="main_page"),

    # login
    path("login/", views.dev_login, name="dev_login"),
    path("logout/", views.dev_logout, name="dev_logout"),

    # Invoices (these fix your base.html links)
    # path("create_invoice/", views.create_invoice, name="create_invoice"),
    path("invoice/sales/create/", views.sales_invoice_create, name="sales_invoice_create"),
    path("invoice/sales/<str:invoice_id>/print/", views.sales_invoice_print, name="sales_invoice_print"),
    path("invoice/sales/<str:invoice_id>/details/", views.sales_invoice_details, name="sales_invoice_details"),
    path("invoice/sales/<str:invoice_id>/update/", views.sales_invoice_update, name="sales_invoice_update"),
    path("invoice/sales/<str:invoice_id>/delete/", views.sales_invoice_delete, name="sales_invoice_delete"),

    # Profiles
    path("profiles/", views.profiles, name="profiles"),

    # Products
    path("profiles/product/create/", views.product_create, name="product_create"),
    path("profiles/product/<str:pk>/update/", views.product_update, name="product_update"),
    path("profiles/product/<str:pk>/delete/", views.product_delete, name="product_delete"),

    # Customers
    path("profiles/customer/create/", views.customer_create, name="customer_create"),
    path("profiles/customer/<str:pk>/update/", views.customer_update, name="customer_update"),
    path("profiles/customer/<str:pk>/delete/", views.customer_delete, name="customer_delete"),

    # Agents
    path("profiles/agent/create/", views.agent_create, name="agent_create"),
    path("profiles/agent/<str:pk>/update/", views.agent_update, name="agent_update"),
    path("profiles/agent/<str:pk>/delete/", views.agent_delete, name="agent_delete"),

    # Banks
    path("profiles/bank/create/", views.bank_create, name="bank_create"),
    path("profiles/bank/<str:pk>/update/", views.bank_update, name="bank_update"),
    path("profiles/bank/<str:pk>/delete/", views.bank_delete, name="bank_delete"),
]
