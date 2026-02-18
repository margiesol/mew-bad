from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator, MaxValueValidator

class Agent(models.Model):
    agent_id = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=100)  # LAST NAME, First Name, M.i.
    phone_no = models.CharField(max_length=13)  # Format: 09XX XXX XXXX
    
    def __str__(self):
        return f"{self.agent_id} - {self.name}"
    
    class Meta:
        db_table = 'AGENT'

class Bank(models.Model):
    bank_id = models.CharField(max_length=4, primary_key=True)
    bank_acronym = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.bank_acronym} - {self.name}"
    
    class Meta:
        db_table = 'BANK'

class Customer(models.Model):
    AREA_CHOICES = [
        # METRO MANILA (16 Cities + 1 Municipality)
        ('Caloocan, Metro Manila', 'Caloocan, Metro Manila'), ('Las Piñas, Metro Manila', 'Las Piñas, Metro Manila'), ('Makati, Metro Manila', 'Makati, Metro Manila'), 
        ('Malabon, Metro Manila', 'Malabon, Metro Manila'), ('Mandaluyong, Metro Manila', 'Mandaluyong, Metro Manila'), ('Manila, Metro Manila', 'Manila, Metro Manila'),
        ('Marikina, Metro Manila', 'Marikina, Metro Manila'), ('Muntinlupa, Metro Manila', 'Muntinlupa, Metro Manila'), ('Navotas, Metro Manila', 'Navotas, Metro Manila'), 
        ('Parañaque, Metro Manila', 'Parañaque, Metro Manila'),
        ('Pasay, Metro Manila', 'Pasay, Metro Manila'), ('Pasig, Metro Manila', 'Pasig, Metro Manila'), ('Quezon City, Metro Manila', 'Quezon City, Metro Manila'), 
        ('San Juan, Metro Manila', 'San Juan, Metro Manila'), ('Taguig, Metro Manila', 'Taguig, Metro Manila'), ('Valenzuela, Metro Manila', 'Valenzuela, Metro Manila'),
        ('Pateros, Metro Manila', 'Pateros, Metro Manila'),
        
        # REGION I - ILOCOS REGION (9 Cities)
        ('Alaminos, Pangasinan', 'Alaminos, Pangasinan'), ('Batac, Ilocos Norte', 'Batac, Ilocos Norte'), ('Candon, Ilocos Sur', 'Candon, Ilocos Sur'),
        ('Dagupan, Pangasinan', 'Dagupan, Pangasinan'), ('Laoag, Ilocos Norte', 'Laoag, Ilocos Norte'), ('San Carlos, Pangasinan', 'San Carlos, Pangasinan'),
        ('San Fernando, La Union', 'San Fernando, La Union'), ('Urdaneta, Pangasinan', 'Urdaneta, Pangasinan'), ('Vigan, Ilocos Sur', 'Vigan, Ilocos Sur'),
        
        # REGION II - CAGAYAN VALLEY (4 Cities)
        ('Cauayan, Isabela', 'Cauayan, Isabela'), ('Ilagan, Isabela', 'Ilagan, Isabela'), ('Santiago, Isabela', 'Santiago, Isabela'),
        ('Tuguegarao, Cagayan', 'Tuguegarao, Cagayan'),
        
        # REGION III - CENTRAL LUZON (13 Cities)
        ('Angeles City, Pampanga', 'Angeles City, Pampanga'), ('Balanga, Bataan', 'Balanga, Bataan'), ('Cabanatuan, Nueva Ecija', 'Cabanatuan, Nueva Ecija'),
        ('Gapan, Nueva Ecija', 'Gapan, Nueva Ecija'), ('Mabalacat, Pampanga', 'Mabalacat, Pampanga'), ('Malolos, Bulacan', 'Malolos, Bulacan'),
        ('Meycauayan, Bulacan', 'Meycauayan, Bulacan'), ('Muñoz, Nueva Ecija', 'Muñoz, Nueva Ecija'), ('Olongapo, Zambales', 'Olongapo, Zambales'),
        ('Palayan, Nueva Ecija', 'Palayan, Nueva Ecija'),
        ('San Fernando, Pampanga', 'San Fernando, Pampanga'), ('San Jose, Nueva Ecija', 'San Jose, Nueva Ecija'), 
        ('San Jose del Monte, Bulacan', 'San Jose del Monte, Bulacan'), ('Tarlac City, Tarlac', 'Tarlac City, Tarlac'),
        
        # REGION IV-A - CALABARZON (19 Cities)
        ('Antipolo, Rizal', 'Antipolo, Rizal'), ('Bacoor, Cavite', 'Bacoor, Cavite'), ('Batangas City, Batangas', 'Batangas City, Batangas'),
        ('Biñan, Laguna', 'Biñan, Laguna'), ('Cabuyao, Laguna', 'Cabuyao, Laguna'), ('Calamba, Laguna', 'Calamba, Laguna'),
        ('Calaca, Batangas', 'Calaca, Batangas'), ('Carmona, Cavite', 'Carmona, Cavite'), ('Cavite City, Cavite', 'Cavite City, Cavite'),
        ('Dasmariñas, Cavite', 'Dasmariñas, Cavite'),
        ('General Trias, Cavite', 'General Trias, Cavite'), ('Imus, Cavite', 'Imus, Cavite'), ('Lipa, Batangas', 'Lipa, Batangas'),
        ('Lucena, Quezon', 'Lucena, Quezon'), ('San Pablo, Laguna', 'San Pablo, Laguna'), ('San Pedro, Laguna', 'San Pedro, Laguna'),
        ('Santa Rosa, Laguna', 'Santa Rosa, Laguna'), ('Santo Tomas, Batangas', 'Santo Tomas, Batangas'), ('Tagaytay, Cavite', 'Tagaytay, Cavite'),
        ('Tanauan, Batangas', 'Tanauan, Batangas'),
        ('Tayabas, Quezon', 'Tayabas, Quezon'), ('Trece Martires, Cavite', 'Trece Martires, Cavite'),
        
        # REGION IV-B - MIMAROPA (2 Cities)
        ('Calapan, Oriental Mindoro', 'Calapan, Oriental Mindoro'), ('Puerto Princesa, Palawan', 'Puerto Princesa, Palawan'),
        
        # REGION V - BICOL REGION (7 Cities)
        ('Iriga, Camarines Sur', 'Iriga, Camarines Sur'), ('Legazpi, Albay', 'Legazpi, Albay'), ('Ligao, Albay', 'Ligao, Albay'),
        ('Masbate City, Masbate', 'Masbate City, Masbate'), ('Naga, Camarines Sur', 'Naga, Camarines Sur'), 
        ('Sorsogon City, Sorsogon', 'Sorsogon City, Sorsogon'), ('Tabaco, Albay', 'Tabaco, Albay'),
        
        # REGION VI - WESTERN VISAYAS (16 Cities)
        ('Bacolod, Negros Occidental', 'Bacolod, Negros Occidental'), ('Bago, Negros Occidental', 'Bago, Negros Occidental'), 
        ('Cadiz, Negros Occidental', 'Cadiz, Negros Occidental'), ('Escalante, Negros Occidental', 'Escalante, Negros Occidental'),
        ('Himamaylan, Negros Occidental', 'Himamaylan, Negros Occidental'), ('Iloilo City, Iloilo', 'Iloilo City, Iloilo'), 
        ('Kabankalan, Negros Occidental', 'Kabankalan, Negros Occidental'), ('La Carlota, Negros Occidental', 'La Carlota, Negros Occidental'),
        ('Passi, Iloilo', 'Passi, Iloilo'), ('Roxas, Capiz', 'Roxas, Capiz'),
        ('Sagay, Negros Occidental', 'Sagay, Negros Occidental'), ('San Carlos, Negros Occidental', 'San Carlos, Negros Occidental'),
        ('Silay, Negros Occidental', 'Silay, Negros Occidental'), ('Sipalay, Negros Occidental', 'Sipalay, Negros Occidental'),
        ('Talisay, Negros Occidental', 'Talisay, Negros Occidental'), ('Victorias, Negros Occidental', 'Victorias, Negros Occidental'),
        
        # REGION VII - CENTRAL VISAYAS (15 Cities)
        ('Bais, Negros Oriental', 'Bais, Negros Oriental'), ('Bayawan, Negros Oriental', 'Bayawan, Negros Oriental'), 
        ('Bogo, Cebu', 'Bogo, Cebu'), ('Canlaon, Negros Oriental', 'Canlaon, Negros Oriental'),
        ('Carcar, Cebu', 'Carcar, Cebu'), ('Cebu City, Cebu', 'Cebu City, Cebu'), ('Danao, Cebu', 'Danao, Cebu'),
        ('Dumaguete, Negros Oriental', 'Dumaguete, Negros Oriental'), ('Guihulngan, Negros Oriental', 'Guihulngan, Negros Oriental'),
        ('Lapu-Lapu, Cebu', 'Lapu-Lapu, Cebu'),
        ('Mandaue, Cebu', 'Mandaue, Cebu'), ('Naga, Cebu', 'Naga, Cebu'), ('San Fernando, Cebu', 'San Fernando, Cebu'),
        ('Talisay, Cebu', 'Talisay, Cebu'), ('Tanjay, Negros Oriental', 'Tanjay, Negros Oriental'), 
        ('Toledo, Cebu', 'Toledo, Cebu'),
        
        # REGION VIII - EASTERN VISAYAS (8 Cities)
        ('Baybay, Leyte', 'Baybay, Leyte'), ('Borongan, Eastern Samar', 'Borongan, Eastern Samar'), 
        ('Calbayog, Samar', 'Calbayog, Samar'), ('Catbalogan, Samar', 'Catbalogan, Samar'),
        ('Maasin, Southern Leyte', 'Maasin, Southern Leyte'), ('Ormoc, Leyte', 'Ormoc, Leyte'), 
        ('Tacloban, Leyte', 'Tacloban, Leyte'),
        
        # REGION IX - ZAMBOANGA PENINSULA (5 Cities)
        ('Dapitan, Zamboanga del Norte', 'Dapitan, Zamboanga del Norte'), ('Dipolog, Zamboanga del Norte', 'Dipolog, Zamboanga del Norte'),
        ('Isabela, Basilan', 'Isabela, Basilan'), ('Pagadian, Zamboanga del Sur', 'Pagadian, Zamboanga del Sur'),
        ('Zamboanga City, Zamboanga del Sur', 'Zamboanga City, Zamboanga del Sur'),
        
        # REGION X - NORTHERN MINDANAO (9 Cities)
        ('Cagayan de Oro, Misamis Oriental', 'Cagayan de Oro, Misamis Oriental'), ('El Salvador, Misamis Oriental', 'El Salvador, Misamis Oriental'),
        ('Gingoog, Misamis Oriental', 'Gingoog, Misamis Oriental'), ('Iligan, Lanao del Norte', 'Iligan, Lanao del Norte'),
        ('Malaybalay, Bukidnon', 'Malaybalay, Bukidnon'), ('Oroquieta, Misamis Occidental', 'Oroquieta, Misamis Occidental'),
        ('Ozamiz, Misamis Occidental', 'Ozamiz, Misamis Occidental'), ('Tangub, Misamis Occidental', 'Tangub, Misamis Occidental'),
        ('Valencia, Bukidnon', 'Valencia, Bukidnon'),
        
        # REGION XI - DAVAO REGION (6 Cities)
        ('Davao City, Davao del Sur', 'Davao City, Davao del Sur'), ('Digos, Davao del Sur', 'Digos, Davao del Sur'),
        ('Mati, Davao Oriental', 'Mati, Davao Oriental'), ('Panabo, Davao del Norte', 'Panabo, Davao del Norte'),
        ('Samal, Davao del Norte', 'Samal, Davao del Norte'), ('Tagum, Davao del Norte', 'Tagum, Davao del Norte'),
        
        # REGION XII - SOCCSKSARGEN (5 Cities)
        ('General Santos, South Cotabato', 'General Santos, South Cotabato'), ('Kidapawan, Cotabato', 'Kidapawan, Cotabato'),
        ('Koronadal, South Cotabato', 'Koronadal, South Cotabato'), ('Tacurong, Sultan Kudarat', 'Tacurong, Sultan Kudarat'),
        
        # REGION XIII - CARAGA (5 Cities)
        ('Bislig, Surigao del Sur', 'Bislig, Surigao del Sur'), ('Butuan, Agusan del Norte', 'Butuan, Agusan del Norte'),
        ('Cabadbaran, Agusan del Norte', 'Cabadbaran, Agusan del Norte'), ('Surigao City, Surigao del Norte', 'Surigao City, Surigao del Norte'),
        ('Tandag, Surigao del Sur', 'Tandag, Surigao del Sur'),
        
        # CORDILLERA ADMINISTRATIVE REGION (2 Cities)
        ('Baguio, Benguet', 'Baguio, Benguet'), ('Tabuk, Kalinga', 'Tabuk, Kalinga'),
        
        # BARMM (3 Cities)
        ('Cotabato City, Maguindanao del Norte', 'Cotabato City, Maguindanao del Norte'), 
        ('Lamitan, Basilan', 'Lamitan, Basilan'), ('Marawi, Lanao del Sur', 'Marawi, Lanao del Sur'),
    ]
    
    customer_id = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=50)  # Company name
    contact_person = models.CharField(max_length=50)  # LAST NAME, First Name, M.i.
    phone_no = models.CharField(max_length=13)  # Format: 09XX XXX XXXX
    address = models.CharField(max_length=150)  # Billing/mailing address
    area = models.CharField(max_length=50, choices=AREA_CHOICES)  # City/Province
    
    def __str__(self):
        return f"{self.customer_id} - {self.name}"
    
    class Meta:
        db_table = 'CUSTOMER'

class Product(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
    product_id = models.CharField(max_length=5, primary_key=True)
    product_code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=150)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    
    def __str__(self):
        return f"{self.product_code} - {self.description}"
    
    class Meta:
        db_table = 'PRODUCTS'

class Sales_Transaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
    ]
    
    invoice_id = models.CharField(max_length=8, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, db_column='agent_id')
    invoice_no = models.CharField(max_length=10, unique=True)
    date = models.DateField()
    plate_no = models.CharField(max_length=10, blank=True, null=True)  # Philippine plate number
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Unpaid')
    partial_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    terms = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    delivery_status = models.BooleanField(default=False)  # 0 = Not Delivered, 1 = Delivered
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
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
    
    def calculate_grand_total(self):
        """Calculate grand total based on orders and returns"""
        return self.total_order_amount - self.total_return_amount - self.discount
    
    def calculate_remaining_balance(self):
        """Calculate remaining balance"""
        return self.grand_total - (self.partial_payment or 0)
    
    def update_payment_status(self):
        """Update payment status based on remaining balance"""
        if self.remaining_balance <= 0:
            self.payment_status = 'Paid'
        elif self.partial_payment and self.partial_payment > 0:
            self.payment_status = 'Partial'
        else:
            self.payment_status = 'Unpaid'
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.grand_total:
            self.grand_total = self.total_order_amount - self.total_return_amount - (self.discount or 0)
        
        self.remaining_balance = self.grand_total - (self.partial_payment or 0)
        
        if self.remaining_balance <= 0:
            self.payment_status = 'Paid'
        elif self.partial_payment and self.partial_payment > 0:
            self.payment_status = 'Partial'
        else:
            self.payment_status = 'Unpaid'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.invoice_no
    
    class Meta:
        db_table = 'SALES_TRANSACTION'

class Order_Record(models.Model):
    invoice = models.ForeignKey(Sales_Transaction, on_delete=models.CASCADE, db_column='invoice_id', related_name='order_records')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    order_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)])
    order_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rate = models.DecimalField(max_digits=3, decimal_places=2, default=1.00, validators=[MinValueValidator(0.00), MaxValueValidator(1.00)])
    
    class Meta:
        unique_together = ['invoice', 'product']
        db_table = 'ORDER_RECORD'
    
    @property
    def total_price(self):
        """Total_Price = Order_Price_per_Unit * Order_Quantity * Rate"""
        return self.order_price_per_unit * self.order_quantity * self.rate
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.save()
    
    def __str__(self):
        return f"{self.invoice.invoice_no} - {self.product.product_code}"

class Return_Record(models.Model):
    invoice = models.ForeignKey(Sales_Transaction, on_delete=models.CASCADE, db_column='invoice_id', related_name='return_records')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    return_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    return_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)])
    rate = models.DecimalField(max_digits=3, decimal_places=2, default=1.00, validators=[MinValueValidator(0.00), MaxValueValidator(1.00)])
    
    class Meta:
        unique_together = ['invoice', 'product']
        db_table = 'RETURN_RECORD'
    
    @property
    def total_price(self):
        """Total_Price = Return_Price_per_Unit * Return_Quantity * Rate"""
        return self.return_price_per_unit * self.return_quantity * self.rate
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.save()
    
    def __str__(self):
        return f"{self.invoice.invoice_no} - {self.product.product_code}"

class Payment_Record(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
    ]
    
    invoice = models.ForeignKey(Sales_Transaction, on_delete=models.CASCADE, db_column='invoice_id', related_name='payment_records')
    payment_record_no = models.CharField(max_length=4, primary_key=True)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    
    class Meta:
        db_table = 'PAYMENT_RECORD'
    
    @property
    def days(self):
        """Days = number of days from invoice date to payment date"""
        if self.payment_date and self.invoice.date:
            return (self.payment_date - self.invoice.date).days
        return 0
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        total_paid = self.invoice.payment_records.aggregate(total=Sum('amount'))['total'] or 0
        self.invoice.partial_payment = total_paid
        self.invoice.save()
    
    def __str__(self):
        return f"{self.invoice.invoice_no} - {self.payment_record_no}"

class Cheque_Payment(models.Model):
    STATUS_CHOICES = [
        ('Valid', 'Valid'),
        ('Bounced', 'Bounced'),
    ]
    
    cq_invoice = models.ForeignKey(Sales_Transaction, on_delete=models.CASCADE, db_column='cq_invoice_id', related_name='cheque_payments')
    cq_payment_record_no = models.CharField(max_length=4, primary_key=True)
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True, db_column='bank_id')
    cq_date = models.DateField()
    cheque_no = models.CharField(max_length=10)  # Set of positive integers
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Valid')
    
    class Meta:
        db_table = 'CHEQUE_PAYMENT'
        unique_together = ['cq_invoice', 'cq_payment_record_no']
    
    def __str__(self):
        return f"{self.cq_invoice.invoice_no} - {self.cheque_no}"

class Account(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return f"User: {self.username}"
    
    class Meta:
        db_table = 'ACCOUNT'