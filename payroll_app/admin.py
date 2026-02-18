from django.contrib import admin
from .models import Account, Product, Customer, Agent, Bank, Sales_Transaction, Order_Record, Payment_Record, Cheque_Payment, Return_Record

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')
    search_fields = ('username',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_code', 'description', 'quantity', 'price', 'status')
    search_fields = ('product_code', 'description')
    list_filter = ('status',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'name', 'contact_person', 'phone_no', 'area')
    search_fields = ('name', 'contact_person', 'phone_no')
    list_filter = ('area',)

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'name', 'phone_no')
    search_fields = ('name',)

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('bank_id', 'bank_acronym', 'name')
    search_fields = ('bank_acronym', 'name')

class OrderRecordInline(admin.TabularInline):
    model = Order_Record
    extra = 1

class ReturnRecordInline(admin.TabularInline):
    model = Return_Record
    extra = 0

class PaymentRecordInline(admin.TabularInline):
    model = Payment_Record
    extra = 0

class ChequePaymentInline(admin.TabularInline):
    model = Cheque_Payment
    extra = 0

@admin.register(Sales_Transaction)
class SalesTransactionAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'invoice_no', 'date', 'customer', 'agent', 
                    'grand_total', 'payment_status', 'delivery_status')
    list_filter = ('payment_status', 'delivery_status', 'date')
    search_fields = ('invoice_no', 'customer__name', 'remarks')
    inlines = [OrderRecordInline, ReturnRecordInline, PaymentRecordInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_id', 'invoice_no', 'date', 'customer', 'agent')
        }),
        ('Delivery Details', {
            'fields': ('plate_no', 'delivery_status')
        }),
        ('Payment Information', {
            'fields': ('grand_total', 'discount', 'partial_payment', 
                      'remaining_balance', 'payment_status')
        }),
        ('Additional Information', {
            'fields': ('terms', 'remarks')
        }),
    )
    
    readonly_fields = ('grand_total', 'remaining_balance', 'payment_status')

@admin.register(Order_Record)
class OrderRecordAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'order_quantity', 'order_price_per_unit', 'rate', 'total_price')
    search_fields = ('invoice__invoice_no', 'product__product_code')

@admin.register(Return_Record)
class ReturnRecordAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'return_quantity', 'return_price_per_unit', 'rate', 'total_price')
    search_fields = ('invoice__invoice_no', 'product__product_code')

@admin.register(Payment_Record)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('payment_record_no', 'invoice', 'payment_date', 'amount', 'payment_type', 'days')
    list_filter = ('payment_type', 'payment_date')
    search_fields = ('invoice__invoice_no', 'payment_record_no')

@admin.register(Cheque_Payment)
class ChequePaymentAdmin(admin.ModelAdmin):
    list_display = ('cq_payment_record_no', 'cq_invoice', 'bank', 'cheque_no', 'cq_date', 'status')
    list_filter = ('status', 'cq_date')
    search_fields = ('cq_invoice__invoice_no', 'cheque_no')