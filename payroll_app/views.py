from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Agent, Bank, Customer, Product, next_padded_id


# --- STUBS to satisfy existing urls.py ---
def home_redirect(request):
    return redirect("main_page")

def dev_login(request):
    request.session["user_id"] = 1
    return redirect("main_page")

def dev_logout(request):
    request.session.pop("user_id", None)
    return redirect("main_page")

def main_page(request):
    active_tab = request.GET.get("tab", "sales")

    context = {
        "active_tab": active_tab,

        # safe defaults so template doesn't error
        "customers": [],
        "suppliers": [],
        "sales_invoices": [],
        "purchase_invoices": [],

        "total_sales": 0,
        "total_sales_received": 0,
        "total_purchases": 0,
        "total_purchases_paid": 0,
    }
    return render(request, "main_page.html", context)



def signup_view(request):
    return HttpResponse("Signup placeholder")


def manage_account(request, pk):
    return HttpResponse(f"Manage account placeholder (pk={pk})")


def delete_account(request, pk):
    return HttpResponse(f"Delete account placeholder (pk={pk})")


def change_password(request, pk):
    return HttpResponse(f"Change password placeholder (pk={pk})")


def create_invoice(request):
    return HttpResponse("Create Invoice placeholder")


def sales_invoice_create(request):
    return HttpResponse("Sales invoice create placeholder")


def sales_invoice_print(request, invoice_id):
    return HttpResponse(f"Sales invoice print placeholder (invoice_id={invoice_id})")


def sales_invoice_details(request, invoice_id):
    return HttpResponse(f"Sales invoice details placeholder (invoice_id={invoice_id})")


# ---------------- PROFILES ----------------
def profiles(request):
    active_tab = request.GET.get("tab", "product")

    products = Product.objects.all().order_by("product_id")
    customers = Customer.objects.all().order_by("customer_id")
    agents = Agent.objects.all().order_by("agent_id")
    banks = Bank.objects.all().order_by("bank_id")

    # ADDED THIS FOR SEARCH
    if active_tab == "product":
        product_code = request.GET.get("product_code")
        description = request.GET.get("description")
        price_input = (request.GET.get("price") or "").strip()
        quantity_input = (request.GET.get("quantity") or "").strip()
        status = request.GET.get("status")

        if product_code:
            products = products.filter(product_code__icontains=product_code)
        if description:
            products = products.filter(description__icontains=description)
        if price_input:
            if '>' in price_input and '<' in price_input:
                try:
                    low = float(price_input.split('>')[1].split('<')[0].strip())
                    high = float(price_input.split('<')[1].strip())
                    products = products.filter(price__gte=low, price__lte=high)
                except (ValueError, IndexError):
                    pass
            elif price_input.startswith('!='):
                try:
                    products = products.exclude(price=float(price_input[2:].strip()))
                except ValueError:
                    pass
            elif price_input.startswith('>'):
                try:
                    products = products.filter(price__gte=float(price_input[1:].strip()))
                except ValueError:
                    pass
            elif price_input.startswith('<'):
                try:
                    products = products.filter(price__lte=float(price_input[1:].strip()))
                except ValueError:
                    pass
            else:
                try:
                    products = products.filter(price=float(price_input))
                except ValueError:
                    pass
        if quantity_input:
            if '>' in quantity_input and '<' in quantity_input:
                try:
                    low = int(quantity_input.split('>')[1].split('<')[0].strip())
                    high = int(quantity_input.split('<')[1].strip())
                    products = products.filter(quantity__gte=low, quantity__lte=high)
                except (ValueError, IndexError):
                    pass
            elif quantity_input.startswith('!='):
                try:
                    products = products.exclude(quantity=int(quantity_input[2:].strip()))
                except ValueError:
                    pass
            elif quantity_input.startswith('>'):
                try:
                    products = products.filter(quantity__gte=int(quantity_input[1:].strip()))
                except ValueError:
                    pass
            elif quantity_input.startswith('<'):
                try:
                    products = products.filter(quantity__lte=int(quantity_input[1:].strip()))
                except ValueError:
                    pass
            else:
                try:
                    products = products.filter(quantity=int(quantity_input))
                except ValueError:
                    pass
        if status and status != "No Selection":
            products = products.filter(status=status)

    if active_tab == "customer":
        customer_id = (request.GET.get("customer_id") or "").strip()
        name = request.GET.get("name")
        contact_person = request.GET.get("contact_person")
        phone_no = (request.GET.get("phone_no") or "").strip()
        area = request.GET.get("area")
        address = request.GET.get("address")

        # Build filter conditions
        if customer_id:
            customers = customers.filter(customer_id__icontains=customer_id)
        if name:
            customers = customers.filter(name__icontains=name)
        if contact_person:
            customers = customers.filter(contact_person__icontains=contact_person)
        if phone_no:
            customers = customers.filter(phone_no__icontains=phone_no)
        if area and area != "No Selection":
            customers = customers.filter(area=area)
        if address:
            customers = customers.filter(address__icontains=address)

    if active_tab == "agent":
        agent_id = (request.GET.get("agent_id") or "").strip()
        name = request.GET.get("name")
        phone_no = (request.GET.get("phone_no") or "").strip()

        # Build filter conditions
        if agent_id:
            agents = agents.filter(agent_id__icontains=agent_id)
        if name:
            agents = agents.filter(name__icontains=name)
        if phone_no:
            agents = agents.filter(phone_no__icontains=phone_no)

    if active_tab == "bank":
        bank_acronym = request.GET.get("bank_acronym")
        name = request.GET.get("name")

        # Build filter conditions
        if bank_acronym:
            banks = banks.filter(bank_acronym__icontains=bank_acronym)
        if name:
            banks = banks.filter(name__icontains=name)
    # ADDED UNTIL HERE ONLY FOR SEARCH  

    context = {
        "active_tab": active_tab,
        "products": products,
        "customers": customers,
        "agents": agents,
        "banks": banks,
        "next_product_id": next_padded_id(Product, "product_id", 5),
        "next_customer_id": next_padded_id(Customer, "customer_id", 4),
        "next_agent_id": next_padded_id(Agent, "agent_id", 4),
        "next_bank_id": next_padded_id(Bank, "bank_id", 4),
        "area_choices": Customer.AREA_CHOICES,
    }
    return render(request, "profiles.html", context)

# ---------------- PRODUCTS ----------------
def product_create(request):
    if request.method == "POST":
        Product.objects.create(
            product_code=request.POST.get("product_code", "").strip(),
            description=request.POST.get("description", "").strip(),
            price=request.POST.get("price") or 0,
            quantity=int(request.POST.get("quantity") or 0),
            status=request.POST.get("status", "Active"),
        )
    return redirect("/profiles/?tab=product")


def product_update(request, pk):
    if request.method == "POST":
        p = get_object_or_404(Product, product_id=pk)
        p.product_code = request.POST.get("product_code", "").strip()
        p.description = request.POST.get("description", "").strip()
        p.price = request.POST.get("price") or 0
        p.quantity = int(request.POST.get("quantity") or 0)
        p.status = request.POST.get("status", "Active")
        p.save()
    return redirect("/profiles/?tab=product")


def product_delete(request, pk):
    if request.method == "POST":
        get_object_or_404(Product, product_id=pk).delete()
    return redirect("/profiles/?tab=product")


# ---------------- CUSTOMERS ----------------
def customer_create(request):
    if request.method == "POST":
        Customer.objects.create(
            name=request.POST.get("name", "").strip(),
            contact_person=request.POST.get("contact_person", "").strip(),
            phone_no=request.POST.get("phone_no", "").strip(),
            address=request.POST.get("address", "").strip(),
            area=request.POST.get("area", "").strip() or "No Selection",
        )
    return redirect("/profiles/?tab=customer")


def customer_update(request, pk):
    if request.method == "POST":
        c = get_object_or_404(Customer, customer_id=pk)
        c.name = request.POST.get("name", "").strip()
        c.contact_person = request.POST.get("contact_person", "").strip()
        c.phone_no = request.POST.get("phone_no", "").strip()
        c.address = request.POST.get("address", "").strip()
        c.area = request.POST.get("area", "").strip() or "No Selection"
        c.save()
    return redirect("/profiles/?tab=customer")


def customer_delete(request, pk):
    if request.method == "POST":
        get_object_or_404(Customer, customer_id=pk).delete()
    return redirect("/profiles/?tab=customer")


# ---------------- AGENTS ----------------
def agent_create(request):
    if request.method == "POST":
        Agent.objects.create(
            name=request.POST.get("name", "").strip(),
            phone_no=request.POST.get("phone_no", "").strip(),
        )
    return redirect("/profiles/?tab=agent")


def agent_update(request, pk):
    if request.method == "POST":
        a = get_object_or_404(Agent, agent_id=pk)
        a.name = request.POST.get("name", "").strip()
        a.phone_no = request.POST.get("phone_no", "").strip()
        a.save()
    return redirect("/profiles/?tab=agent")


def agent_delete(request, pk):
    if request.method == "POST":
        get_object_or_404(Agent, agent_id=pk).delete()
    return redirect("/profiles/?tab=agent")


# ---------------- BANKS ----------------
def bank_create(request):
    if request.method == "POST":
        Bank.objects.create(
            bank_acronym=request.POST.get("bank_acronym", "").strip(),
            name=request.POST.get("name", "").strip(),
        )
    return redirect("/profiles/?tab=bank")


def bank_update(request, pk):
    if request.method == "POST":
        b = get_object_or_404(Bank, bank_id=pk)
        b.bank_acronym = request.POST.get("bank_acronym", "").strip()
        b.name = request.POST.get("name", "").strip()
        b.save()
    return redirect("/profiles/?tab=bank")


def bank_delete(request, pk):
    if request.method == "POST":
        get_object_or_404(Bank, bank_id=pk).delete()
    return redirect("/profiles/?tab=bank")