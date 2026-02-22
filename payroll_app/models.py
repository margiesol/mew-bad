from django.db import models
from django.db.models import Max, Sum
from django.db import transaction
from datetime import date, datetime

from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

def next_padded_id(model_cls, field_name: str, width: int) -> str:
    # If you have multiple users, consider select_for_update on databases that support it.
    current_max = model_cls.objects.aggregate(m=Max(field_name))["m"]
    if not current_max:
        return str(1).zfill(width)
    return str(int(current_max) + 1).zfill(width)


class Agent(models.Model):
    agent_id = models.CharField(max_length=4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=13)

    class Meta:
        db_table = "AGENT"

    def save(self, *args, **kwargs):
        if not self.agent_id:
            self.agent_id = next_padded_id(Agent, "agent_id", 4)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.agent_id} - {self.name}"


class Bank(models.Model):
    bank_id = models.CharField(max_length=4, primary_key=True, editable=False)
    bank_acronym = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "BANK"

    def save(self, *args, **kwargs):
        if not self.bank_id:
            self.bank_id = next_padded_id(Bank, "bank_id", 4)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bank_acronym} - {self.name}"


class Customer(models.Model):

    AREA_CHOICES = [
        ("No Selection", "No Selection"),

        # METRO MANILA
        ('Caloocan, Metro Manila', 'Caloocan, Metro Manila'),
        ('Las Piñas, Metro Manila', 'Las Piñas, Metro Manila'),
        ('Makati, Metro Manila', 'Makati, Metro Manila'),
        ('Malabon, Metro Manila', 'Malabon, Metro Manila'),
        ('Mandaluyong, Metro Manila', 'Mandaluyong, Metro Manila'),
        ('Manila, Metro Manila', 'Manila, Metro Manila'),
        ('Marikina, Metro Manila', 'Marikina, Metro Manila'),
        ('Muntinlupa, Metro Manila', 'Muntinlupa, Metro Manila'),
        ('Navotas, Metro Manila', 'Navotas, Metro Manila'),
        ('Parañaque, Metro Manila', 'Parañaque, Metro Manila'),
        ('Pasay, Metro Manila', 'Pasay, Metro Manila'),
        ('Pasig, Metro Manila', 'Pasig, Metro Manila'),
        ('Quezon City, Metro Manila', 'Quezon City, Metro Manila'),
        ('San Juan, Metro Manila', 'San Juan, Metro Manila'),
        ('Taguig, Metro Manila', 'Taguig, Metro Manila'),
        ('Valenzuela, Metro Manila', 'Valenzuela, Metro Manila'),
        ('Pateros, Metro Manila', 'Pateros, Metro Manila'),

        # REGION I
        ('Alaminos, Pangasinan', 'Alaminos, Pangasinan'),
        ('Batac, Ilocos Norte', 'Batac, Ilocos Norte'),
        ('Candon, Ilocos Sur', 'Candon, Ilocos Sur'),
        ('Dagupan, Pangasinan', 'Dagupan, Pangasinan'),
        ('Laoag, Ilocos Norte', 'Laoag, Ilocos Norte'),
        ('San Carlos, Pangasinan', 'San Carlos, Pangasinan'),
        ('San Fernando, La Union', 'San Fernando, La Union'),
        ('Urdaneta, Pangasinan', 'Urdaneta, Pangasinan'),
        ('Vigan, Ilocos Sur', 'Vigan, Ilocos Sur'),

        # REGION II
        ('Cauayan, Isabela', 'Cauayan, Isabela'),
        ('Ilagan, Isabela', 'Ilagan, Isabela'),
        ('Santiago, Isabela', 'Santiago, Isabela'),
        ('Tuguegarao, Cagayan', 'Tuguegarao, Cagayan'),

        # REGION III
        ('Angeles City, Pampanga', 'Angeles City, Pampanga'),
        ('Balanga, Bataan', 'Balanga, Bataan'),
        ('Cabanatuan, Nueva Ecija', 'Cabanatuan, Nueva Ecija'),
        ('Gapan, Nueva Ecija', 'Gapan, Nueva Ecija'),
        ('Mabalacat, Pampanga', 'Mabalacat, Pampanga'),
        ('Malolos, Bulacan', 'Malolos, Bulacan'),
        ('Meycauayan, Bulacan', 'Meycauayan, Bulacan'),
        ('Muñoz, Nueva Ecija', 'Muñoz, Nueva Ecija'),
        ('Olongapo, Zambales', 'Olongapo, Zambales'),
        ('Palayan, Nueva Ecija', 'Palayan, Nueva Ecija'),
        ('San Fernando, Pampanga', 'San Fernando, Pampanga'),
        ('San Jose, Nueva Ecija', 'San Jose, Nueva Ecija'),
        ('San Jose del Monte, Bulacan', 'San Jose del Monte, Bulacan'),
        ('Tarlac City, Tarlac', 'Tarlac City, Tarlac'),

        # REGION IV-A
        ('Antipolo, Rizal', 'Antipolo, Rizal'),
        ('Bacoor, Cavite', 'Bacoor, Cavite'),
        ('Batangas City, Batangas', 'Batangas City, Batangas'),
        ('Biñan, Laguna', 'Biñan, Laguna'),
        ('Cabuyao, Laguna', 'Cabuyao, Laguna'),
        ('Calamba, Laguna', 'Calamba, Laguna'),
        ('Calaca, Batangas', 'Calaca, Batangas'),
        ('Carmona, Cavite', 'Carmona, Cavite'),
        ('Cavite City, Cavite', 'Cavite City, Cavite'),
        ('Dasmariñas, Cavite', 'Dasmariñas, Cavite'),
        ('General Trias, Cavite', 'General Trias, Cavite'),
        ('Imus, Cavite', 'Imus, Cavite'),
        ('Lipa, Batangas', 'Lipa, Batangas'),
        ('Lucena, Quezon', 'Lucena, Quezon'),
        ('San Pablo, Laguna', 'San Pablo, Laguna'),
        ('San Pedro, Laguna', 'San Pedro, Laguna'),
        ('Santa Rosa, Laguna', 'Santa Rosa, Laguna'),
        ('Santo Tomas, Batangas', 'Santo Tomas, Batangas'),
        ('Tagaytay, Cavite', 'Tagaytay, Cavite'),
        ('Tanauan, Batangas', 'Tanauan, Batangas'),
        ('Tayabas, Quezon', 'Tayabas, Quezon'),
        ('Trece Martires, Cavite', 'Trece Martires, Cavite'),

        # REGION IV-B
        ('Calapan, Oriental Mindoro', 'Calapan, Oriental Mindoro'),
        ('Puerto Princesa, Palawan', 'Puerto Princesa, Palawan'),

        # REGION V
        ('Iriga, Camarines Sur', 'Iriga, Camarines Sur'),
        ('Legazpi, Albay', 'Legazpi, Albay'),
        ('Ligao, Albay', 'Ligao, Albay'),
        ('Masbate City, Masbate', 'Masbate City, Masbate'),
        ('Naga, Camarines Sur', 'Naga, Camarines Sur'),
        ('Sorsogon City, Sorsogon', 'Sorsogon City, Sorsogon'),
        ('Tabaco, Albay', 'Tabaco, Albay'),

        # REGION VI
        ('Bacolod, Negros Occidental', 'Bacolod, Negros Occidental'),
        ('Bago, Negros Occidental', 'Bago, Negros Occidental'),
        ('Cadiz, Negros Occidental', 'Cadiz, Negros Occidental'),
        ('Escalante, Negros Occidental', 'Escalante, Negros Occidental'),
        ('Himamaylan, Negros Occidental', 'Himamaylan, Negros Occidental'),
        ('Iloilo City, Iloilo', 'Iloilo City, Iloilo'),
        ('Kabankalan, Negros Occidental', 'Kabankalan, Negros Occidental'),
        ('La Carlota, Negros Occidental', 'La Carlota, Negros Occidental'),
        ('Passi, Iloilo', 'Passi, Iloilo'),
        ('Roxas, Capiz', 'Roxas, Capiz'),
        ('Sagay, Negros Occidental', 'Sagay, Negros Occidental'),
        ('San Carlos, Negros Occidental', 'San Carlos, Negros Occidental'),
        ('Silay, Negros Occidental', 'Silay, Negros Occidental'),
        ('Sipalay, Negros Occidental', 'Sipalay, Negros Occidental'),
        ('Talisay, Negros Occidental', 'Talisay, Negros Occidental'),
        ('Victorias, Negros Occidental', 'Victorias, Negros Occidental'),

        # REGION VII
        ('Bais, Negros Oriental', 'Bais, Negros Oriental'),
        ('Bayawan, Negros Oriental', 'Bayawan, Negros Oriental'),
        ('Bogo, Cebu', 'Bogo, Cebu'),
        ('Canlaon, Negros Oriental', 'Canlaon, Negros Oriental'),
        ('Carcar, Cebu', 'Carcar, Cebu'),
        ('Cebu City, Cebu', 'Cebu City, Cebu'),
        ('Danao, Cebu', 'Danao, Cebu'),
        ('Dumaguete, Negros Oriental', 'Dumaguete, Negros Oriental'),
        ('Guihulngan, Negros Oriental', 'Guihulngan, Negros Oriental'),
        ('Lapu-Lapu, Cebu', 'Lapu-Lapu, Cebu'),
        ('Mandaue, Cebu', 'Mandaue, Cebu'),
        ('Naga, Cebu', 'Naga, Cebu'),
        ('San Fernando, Cebu', 'San Fernando, Cebu'),
        ('Talisay, Cebu', 'Talisay, Cebu'),
        ('Tanjay, Negros Oriental', 'Tanjay, Negros Oriental'),
        ('Toledo, Cebu', 'Toledo, Cebu'),

        # REGION VIII
        ('Baybay, Leyte', 'Baybay, Leyte'),
        ('Borongan, Eastern Samar', 'Borongan, Eastern Samar'),
        ('Calbayog, Samar', 'Calbayog, Samar'),
        ('Catbalogan, Samar', 'Catbalogan, Samar'),
        ('Maasin, Southern Leyte', 'Maasin, Southern Leyte'),
        ('Ormoc, Leyte', 'Ormoc, Leyte'),
        ('Tacloban, Leyte', 'Tacloban, Leyte'),

        # REGION IX
        ('Dapitan, Zamboanga del Norte', 'Dapitan, Zamboanga del Norte'),
        ('Dipolog, Zamboanga del Norte', 'Dipolog, Zamboanga del Norte'),
        ('Isabela, Basilan', 'Isabela, Basilan'),
        ('Pagadian, Zamboanga del Sur', 'Pagadian, Zamboanga del Sur'),
        ('Zamboanga City, Zamboanga del Sur', 'Zamboanga City, Zamboanga del Sur'),

        # REGION X
        ('Cagayan de Oro, Misamis Oriental', 'Cagayan de Oro, Misamis Oriental'),
        ('El Salvador, Misamis Oriental', 'El Salvador, Misamis Oriental'),
        ('Gingoog, Misamis Oriental', 'Gingoog, Misamis Oriental'),
        ('Iligan, Lanao del Norte', 'Iligan, Lanao del Norte'),
        ('Malaybalay, Bukidnon', 'Malaybalay, Bukidnon'),
        ('Oroquieta, Misamis Occidental', 'Oroquieta, Misamis Occidental'),
        ('Ozamiz, Misamis Occidental', 'Ozamiz, Misamis Occidental'),
        ('Tangub, Misamis Occidental', 'Tangub, Misamis Occidental'),
        ('Valencia, Bukidnon', 'Valencia, Bukidnon'),

        # REGION XI
        ('Davao City, Davao del Sur', 'Davao City, Davao del Sur'),
        ('Digos, Davao del Sur', 'Digos, Davao del Sur'),
        ('Mati, Davao Oriental', 'Mati, Davao Oriental'),
        ('Panabo, Davao del Norte', 'Panabo, Davao del Norte'),
        ('Samal, Davao del Norte', 'Samal, Davao del Norte'),
        ('Tagum, Davao del Norte', 'Tagum, Davao del Norte'),

        # REGION XII
        ('General Santos, South Cotabato', 'General Santos, South Cotabato'),
        ('Kidapawan, Cotabato', 'Kidapawan, Cotabato'),
        ('Koronadal, South Cotabato', 'Koronadal, South Cotabato'),
        ('Tacurong, Sultan Kudarat', 'Tacurong, Sultan Kudarat'),

        # REGION XIII
        ('Bislig, Surigao del Sur', 'Bislig, Surigao del Sur'),
        ('Butuan, Agusan del Norte', 'Butuan, Agusan del Norte'),
        ('Cabadbaran, Agusan del Norte', 'Cabadbaran, Agusan del Norte'),
        ('Surigao City, Surigao del Norte', 'Surigao City, Surigao del Norte'),
        ('Tandag, Surigao del Sur', 'Tandag, Surigao del Sur'),

        # CAR
        ('Baguio, Benguet', 'Baguio, Benguet'),
        ('Tabuk, Kalinga', 'Tabuk, Kalinga'),

        # BARMM
        ('Cotabato City, Maguindanao del Norte', 'Cotabato City, Maguindanao del Norte'),
        ('Lamitan, Basilan', 'Lamitan, Basilan'),
        ('Marawi, Lanao del Sur', 'Marawi, Lanao del Sur'),
    ]

    customer_id = models.CharField(max_length=4, primary_key=True, editable=False)
    name = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=13)
    address = models.CharField(max_length=150)

    # IMPORTANT: longer max_length because your choices are long strings
    area = models.CharField(
        max_length=100,
        choices=AREA_CHOICES,
        default="No Selection",
        blank=True,
    )

    class Meta:
        db_table = "CUSTOMER"

    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer_id = next_padded_id(Customer, "customer_id", 4)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_id} - {self.name}"


class Product(models.Model):
    STATUS_CHOICES = [("Active", "Active"), ("Inactive", "Inactive")]

    product_id = models.CharField(max_length=5, primary_key=True, editable=False)
    product_code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=150)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="Active")

    class Meta:
        db_table = "PRODUCTS"

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = next_padded_id(Product, "product_id", 5)  # 00001
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_code} - {self.description}"
    
# ==================== SALES INVOICE MODELS ADDED BY MAI ====================
# ----------------------------
# Helpers for ID generation
# ----------------------------
def _next_numeric_char_pk(model_cls, field_name: str, width: int) -> str:
    """
    For CHAR PKs that are numeric strings like '00000001' (width=8).
    """
    current_max = model_cls.objects.aggregate(m=Max(field_name))["m"]
    if not current_max:
        return str(1).zfill(width)
    try:
        return str(int(current_max) + 1).zfill(width)
    except ValueError:
        # fallback if somehow non-numeric got stored
        return str(1).zfill(width)

# ==========================================================
# SALES_TRANSACTION  (Invoice model)
# ==========================================================
class SalesInvoice(models.Model):
    """
    Matches ERD: SALES_TRANSACTION
    PK: Invoice_ID (CHAR8) - auto-incremented
    """

    PAYMENT_STATUS_CHOICES = [
        ("Unpaid", "Unpaid"),
        ("Partial", "Partial"),
        ("Paid", "Paid"),
    ]

    invoice_id = models.CharField(
        max_length=8,
        primary_key=True,
        editable=False,
        db_column="Invoice_ID",
    )

    customer = models.ForeignKey(
        "Customer",
        on_delete=models.PROTECT,
        db_column="Customer_ID",
        related_name="sales_invoices",
    )

    agent = models.ForeignKey(
        "Agent",
        on_delete=models.PROTECT,
        db_column="Agent_ID",
        related_name="sales_invoices",
    )

    # This is just for display - not used as primary key
    invoice_no = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        db_column="Invoice_No",
    )

    date = models.DateField(default=timezone.localdate, db_column="Date")
    plate_no = models.CharField(max_length=10, blank=True, default="", db_column="Plate_No")

    # Derived / computed (ERD bracketed)
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="Unpaid",
        editable=False,
        db_column="Payment_Status",
    )

    partial_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        db_column="Partial_Payment",
    )

    terms = models.CharField(max_length=50, null=True, blank=True, db_column="Terms")
    remarks = models.CharField(max_length=255, null=True, blank=True, db_column="Remarks")

    delivery_status = models.BooleanField(default=False, db_column="Delivery_Status")

    # Derived / computed
    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        db_column="Grand_Total",
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        db_column="Discount",
    )

    # Derived / computed
    remaining_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        db_column="Remaining_Balance",
    )

    is_deleted = models.BooleanField(default=False, db_column="Is_Deleted")
    deleted_at = models.DateTimeField(null=True, blank=True, db_column="Deleted_At")

    class Meta:
        db_table = "SALES_TRANSACTION"

    @classmethod
    def _next_invoice_no(cls) -> str:
        """
        Generate display invoice number in format: YYOF000001
        This is just for display, not used as primary key
        """
        yy = str(timezone.localdate().year)[-2:]
        prefix = f"{yy}OF"

        max_invoice_no = (
            cls.objects
            .filter(invoice_no__startswith=prefix)
            .aggregate(m=Max("invoice_no"))["m"]
        )

        if max_invoice_no:
            try:
                last_num = int(max_invoice_no[4:])  # after YYOF
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1

        return f"{prefix}{str(next_num).zfill(6)}"

    def _recompute(self):
        """
        Computes:
        - grand_total = sum(order_record.total_price) - sum(return_record.total_price) - discount
        - partial_payment = sum(payment_record.amount)
        - remaining_balance = grand_total - partial_payment
        - payment_status based on remaining_balance
        """
        order_total = self.order_records.aggregate(s=Sum("total_price"))["s"] or Decimal("0.00")
        return_total = self.return_records.aggregate(s=Sum("total_price"))["s"] or Decimal("0.00")
        discount = Decimal(self.discount or 0)

        grand = (Decimal(order_total) - Decimal(return_total)) - discount
        if grand < 0:
            grand = Decimal("0.00")
        self.grand_total = grand.quantize(Decimal("0.01"))

        paid = self.payment_records.aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
        self.partial_payment = Decimal(paid).quantize(Decimal("0.01"))

        bal = (self.grand_total - self.partial_payment).quantize(Decimal("0.01"))
        if bal < 0:
            bal = Decimal("0.00")
        self.remaining_balance = bal

        if self.grand_total == Decimal("0.00"):
            self.payment_status = "Paid"
        elif self.partial_payment <= Decimal("0.00"):
            self.payment_status = "Unpaid"
        elif self.remaining_balance == Decimal("0.00"):
            self.payment_status = "Paid"
        else:
            self.payment_status = "Partial"

    def save(self, *args, **kwargs):
        # Generate auto-incremented invoice_id first
        if not self.invoice_id:
            self.invoice_id = _next_numeric_char_pk(SalesInvoice, "invoice_id", 8)
        
        # Generate display invoice_no (YYOF000001) - this is just for humans to read
        if not self.invoice_no:
            self.invoice_no = SalesInvoice._next_invoice_no()

        # compute derived fields before saving
        self._recompute()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_no} ({self.invoice_id})"

# ==========================================================
# ORDER_RECORD
# PK in ERD: (Invoice_ID, Product_ID)  -> enforced via UniqueConstraint
# ==========================================================
class OrderRecord(models.Model):
    invoice = models.ForeignKey(
        "SalesInvoice",
        on_delete=models.CASCADE,
        db_column="Invoice_ID",
        related_name="order_records",
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.PROTECT,
        db_column="Product_ID",
        related_name="order_records",
    )

    order_quantity = models.PositiveIntegerField(default=0, db_column="Order_Quantity")

    order_price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        db_column="Order_Price_per_Unit",
    )

    # Rate <= 1 (from your ERD)
    rate = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))],
        db_column="Rate",
    )

    # Derived: [Total_Price]
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        db_column="Total_Price",
    )

    class Meta:
        db_table = "ORDER_RECORD"
        constraints = [
            models.UniqueConstraint(fields=["invoice", "product"], name="uq_order_invoice_product")
        ]

    def save(self, *args, **kwargs):
        qty = Decimal(self.order_quantity or 0)
        ppu = Decimal(self.order_price_per_unit or 0)
        r = Decimal(self.rate or 0)
        self.total_price = (qty * ppu * r).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

        # update invoice computed totals/status
        self.invoice.save()

    def __str__(self):
        return f"ORDER_RECORD invoice={self.invoice_id} product={self.product_id}"


# ==========================================================
# RETURN_RECORD
# PK in ERD: (Invoice_ID, Product_ID)  -> enforced via UniqueConstraint
# ==========================================================
class ReturnRecord(models.Model):
    invoice = models.ForeignKey(
        "SalesInvoice",
        on_delete=models.CASCADE,
        db_column="Invoice_ID",
        related_name="return_records",
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.PROTECT,
        db_column="Product_ID",
        related_name="return_records",
    )

    return_quantity = models.PositiveIntegerField(default=0, db_column="Return_Quantity")

    return_price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        db_column="Return_Price_per_Unit",
    )

    # Rate <= 1
    rate = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))],
        db_column="Rate",
    )

    # Derived: [Total_Price]
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        db_column="Total_Price",
    )

    class Meta:
        db_table = "RETURN_RECORD"
        constraints = [
            models.UniqueConstraint(fields=["invoice", "product"], name="uq_return_invoice_product")
        ]

    def save(self, *args, **kwargs):
        qty = Decimal(self.return_quantity or 0)
        ppu = Decimal(self.return_price_per_unit or 0)
        r = Decimal(self.rate or 0)
        self.total_price = (qty * ppu * r).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

        # update invoice computed totals/status
        self.invoice.save()

    def __str__(self):
        return f"RETURN_RECORD invoice={self.invoice_id} product={self.product_id}"


# ==========================================================
# PAYMENT_RECORD
# PK in ERD: (Invoice_ID, Payment_Record_No) -> enforced via UniqueConstraint
# ==========================================================
class PaymentRecord(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ("Cash", "Cash"),
        ("Cheque", "Cheque"),
    ]

    invoice = models.ForeignKey(
        "SalesInvoice",
        on_delete=models.CASCADE,
        db_column="Invoice_ID",
        related_name="payment_records",
    )

    payment_record_no = models.CharField(
        max_length=4,
        editable=False,
        db_column="Payment_Record_No",
    )

    payment_date = models.DateField(default=timezone.localdate, db_column="Payment_Date")

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        db_column="Amount",
    )

    # Derived: [Days] = payment_date - invoice.date
    days = models.IntegerField(default=0, editable=False, db_column="Days")

    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_TYPE_CHOICES,
        db_column="Payment_Type",
    )

    class Meta:
        db_table = "PAYMENT_RECORD"
        constraints = [
            models.UniqueConstraint(
                fields=["invoice", "payment_record_no"],
                name="uq_payment_invoice_recordno",
            )
        ]

    def _next_payment_record_no(self) -> str:
        max_no = (
            PaymentRecord.objects
            .filter(invoice=self.invoice)
            .aggregate(m=Max("payment_record_no"))["m"]
        )
        if not max_no:
            return str(1).zfill(4)
        try:
            return str(int(max_no) + 1).zfill(4)
        except ValueError:
            return str(1).zfill(4)

    def save(self, *args, **kwargs):
        if not self.payment_record_no:
            self.payment_record_no = self._next_payment_record_no()

        inv_date = self.invoice.date
        pay_date = self.payment_date
        self.days = max((pay_date - inv_date).days, 0)

        super().save(*args, **kwargs)

        # update invoice computed totals/status
        self.invoice.save()

    def __str__(self):
        return f"PAYMENT_RECORD {self.payment_record_no} invoice={self.invoice_id}"


# ==========================================================
# CHEQUE_PAYMENT (in ERD; ties to PaymentRecord)
# composite PK in ERD: (CQ_Invoice_ID, CQ_Payment_Record_No)
# We enforce uniqueness instead.
# ==========================================================
class ChequePayment(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Cleared", "Cleared"),
        ("Bounced", "Bounced"),
    ]

    # tie to PaymentRecord (Invoice_ID + Payment_Record_No)
    payment_record = models.OneToOneField(
        "PaymentRecord",
        on_delete=models.CASCADE,
        related_name="cheque_detail",
    )

    bank = models.ForeignKey(
        "Bank",
        on_delete=models.PROTECT,
        db_column="Bank_ID",
        related_name="cheque_payments",
    )

    cq_date = models.DateField(default=timezone.localdate, db_column="CQ_Date")
    cheque_no = models.CharField(max_length=10, db_column="Cheque_No")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending", db_column="Status")

    class Meta:
        db_table = "CHEQUE_PAYMENT"

    def __str__(self):
        return f"CHEQUE_PAYMENT invoice={self.payment_record.invoice_id} pr={self.payment_record.payment_record_no}"