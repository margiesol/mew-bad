from django.db import models
from django.db.models import Max
from django.db import transaction


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
