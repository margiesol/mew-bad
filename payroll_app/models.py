from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, fields

class Account(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return f"User: {self.username}"

class Customer(models.Model):
    #customer_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField(null=True, blank=True, unique=True)  # TEMP business id
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.customer_id} - {self.name}"

class Agent(models.Model):
    agent_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    #product_id = models.AutoField(primary_key=True)
    product_id = models.IntegerField(null=True, blank=True, unique=True)  # TEMP business id (not PK)
    product_code = models.CharField(max_length=50, unique=True)
    quantity = models.IntegerField(default=0)
    description = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Active')
    unit = models.CharField(max_length=20, default='PCS')
    
    def __str__(self):
        return f"{self.product_code} - {self.description}"

class SalesTransaction(models.Model): 
    TERMS_CHOICES = [
        (30, '30 days'),
        (60, '60 days'),
        (90, '90 days'),
    ]
       
    invoice_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales_transactions')
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_no = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    plate_no = models.CharField(max_length=20, blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    delivery_status = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_order_amount(self):
        """Total from all order records (Order_Price_per_Unit * Order_Quantity * Rate)"""
        total = self.order_records.aggregate(
            total=Sum(F('order_quantity') * F('order_price_per_unit') * F('rate'))
        )['total'] or 0
        return total
    
    @property
    def total_return_amount(self):
        """Total from all return records (Return_Price_per_Unit * Return_Quantity * Rate)"""
        total = self.return_records.aggregate(
            total=Sum(F('return_quantity') * F('return_price_per_unit') * F('rate'))
        )['total'] or 0
        return total
    
    @property
    def grand_total(self):
        """Grand_Total = total_order_amount - total_return_amount"""
        return self.total_order_amount - self.total_return_amount
    
    @property
    def partial_payment(self):
        """Total amount paid so far from payment records"""
        total = self.payment_records.aggregate(total=Sum('amount'))['total'] or 0
        return total
    
    @property
    def remaining_balance(self):
        """Remaining_Balance = grand_total - partial_payment"""
        return self.grand_total - self.partial_payment
    
    @property
    def payment_status(self):
        """Payment_Status: unpaid, partial, or paid based on remaining_balance"""
        if self.remaining_balance <= 0:
            return 'paid'
        elif self.partial_payment > 0:
            return 'partial'
        else:
            return 'unpaid'
    
    def __str__(self):
        return self.invoice_no

class OrderRecord(models.Model):
    invoice = models.ForeignKey(SalesTransaction, on_delete=models.CASCADE, related_name='order_records')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_quantity = models.IntegerField(default=1)
    order_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=2, decimal_places=2, default=1)
    
    class Meta:
        unique_together = ['invoice', 'product']
    
    @property
    def total_price(self):
        """Total_Price = Order_Price_per_Unit * Order_Quantity * Rate"""
        return self.order_price_per_unit * self.order_quantity * self.rate
    
    def __str__(self):
        return f"{self.invoice.invoice_no} - {self.product.product_code}"

class PaymentRecord(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ]
    
    invoice = models.ForeignKey(SalesTransaction, on_delete=models.CASCADE, related_name='payment_records')
    payment_record_no = models.CharField(max_length=50)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='cash')
    
    class Meta:
        unique_together = ['invoice', 'payment_record_no']
    
    @property
    def days(self):
        """Days = number of days from invoice date to payment/cheque date"""
        if self.payment_date and self.invoice.date:
            return (self.payment_date - self.invoice.date).days
        return 0
    
    def __str__(self):
        return f"{self.invoice.invoice_no} - {self.payment_record_no}"

class ChequePayment(models.Model):
    STATUS_CHOICES = [
        ('valid', 'Valid'),
        ('bounced', 'Bounced'),
    ]
    
    cq_invoice = models.ForeignKey(SalesTransaction, on_delete=models.CASCADE, related_name='cheque_payments')
    cq_payment_record_no = models.CharField(max_length=50)
    bank = models.ForeignKey('Bank', on_delete=models.SET_NULL, null=True)
    cq_date = models.DateField()
    cheque_no = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ['cq_invoice', 'cq_payment_record_no']
    
    def __str__(self):
        return f"{self.cq_invoice.invoice_no} - {self.cheque_no}"

class Bank(models.Model):
    bank_id = models.AutoField(primary_key=True)
    bank_acronym = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.bank_acronym} - {self.name}"

class ReturnRecord(models.Model):
    invoice = models.ForeignKey(SalesTransaction, on_delete=models.CASCADE, related_name='return_records')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    return_quantity = models.IntegerField(default=1)
    return_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=1)  # Multiplier factor
    
    class Meta:
        unique_together = ['invoice', 'product']
    
    @property
    def total_price(self):
        """Total_Price = Return_Price_per_Unit * Return_Quantity * Rate"""
        return self.return_price_per_unit * self.return_quantity * self.rate
    
    def __str__(self):
        return f"{self.invoice.invoice_no} - {self.product.product_code}"