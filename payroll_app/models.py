from django.db import models

class Account(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return f"User: {self.username}"

class Customer(models.Model):
    customer_code = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.customer_code} - {self.company_name}"
    
class Supplier(models.Model):
    supplier_code = models.CharField(max_length=50, unique=True)
    supplier_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, default='N/A')
    supplier_address = models.TextField(default='N/A')
    phone = models.CharField(max_length=20, default='N/A')
    area = models.CharField(max_length=100, default='N/A')
    
    def __str__(self):
        return f"{self.supplier_code} - {self.supplier_name}"

class Product(models.Model):
    product_code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='PCS')
    
    def __str__(self):
        return f"{self.product_code} - {self.description}"

class SalesInvoice(models.Model):
    PAYMENT_TYPES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    plate_no = models.CharField(max_length=20, blank=True, null=True)
    
    # Payment Information
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES, default='cash')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_received = models.BooleanField(default=False)
    
    # Totals
    invoice_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(SalesInvoice, related_name='items', on_delete=models.CASCADE)
    product_code = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=20, default='PCS')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product_code} - {self.description}"

class PurchaseInvoice(models.Model):
    PAYMENT_TYPES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True)
    invoice_date = models.DateField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES, default='cash')
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Totals
    invoice_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.invoice_number

class PurchaseInvoiceItem(models.Model):
    invoice = models.ForeignKey(PurchaseInvoice, related_name='items', on_delete=models.CASCADE)
    product_code = models.CharField(max_length=50)
    description = models.TextField()
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=20, default='PCS')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product_code} - {self.description}"