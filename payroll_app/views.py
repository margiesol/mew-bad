from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime

from .models import Agent, Bank, Customer, Product, next_padded_id, SalesInvoice, PaymentRecord, OrderRecord, ReturnRecord, ChequePayment

# --- STUBS to satisfy existing urls.py ---
def home_redirect(request):
    return redirect("main_page")

def dev_login(request):
    request.session["user_id"] = 1
    return redirect("main_page")

def dev_logout(request):
    request.session.pop("user_id", None)
    return redirect("main_page")

# def main_page(request):
#     active_tab = request.GET.get("tab", "sales")

#     context = {
#         "active_tab": active_tab,

#         # safe defaults so template doesn't error
#         "customers": [],
#         "suppliers": [],
#         "sales_invoices": [],
#         "purchase_invoices": [],

#         "total_sales": 0,
#         "total_sales_received": 0,
#         "total_purchases": 0,
#         "total_purchases_paid": 0,
#     }
#     return render(request, "main_page.html", context)

# ADDED BY MAI
def main_page(request):
    active_tab = request.GET.get("tab", "sales")
    
    # Get all sales invoices
    sales_invoices = SalesInvoice.objects.all().order_by('-date', '-invoice_no')
    
    # Calculate totals
    total_sales = sales_invoices.aggregate(total=Sum('grand_total'))['total'] or 0
    total_sales_received = sales_invoices.filter(payment_status='Paid').aggregate(total=Sum('grand_total'))['total'] or 0
    
    context = {
        "active_tab": active_tab,
        "customers": Customer.objects.all(),
        "sales_invoices": sales_invoices,
        "total_sales": total_sales,
        "total_sales_received": total_sales_received,
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

# COMMENTED THESE OUT FOR NOW TO AVOID ERRORS, CHECK BOTTOM OF THIS FILE FOR RELEVANT VIEWS
# def create_invoice(request):
#     return render(request, 'invoice.html')


# def sales_invoice_create(request):
#     return HttpResponse("Sales invoice create placeholder")


# def sales_invoice_print(request, invoice_id):
#     return HttpResponse(f"Sales invoice print placeholder (invoice_id={invoice_id})")


# def sales_invoice_details(request, invoice_id):
#     return HttpResponse(f"Sales invoice details placeholder (invoice_id={invoice_id})")


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

# ---------------- INVOICE VIEWS ADDED BY MAI ----------------
def sales_invoice_create(request):
    if request.method == "POST":
        # Get basic form data
        invoice_number = request.POST.get("invoice_number")
        invoice_date_str = request.POST.get("invoice_date")
        plate_no = request.POST.get("plate_no", "")
        terms = request.POST.get("terms", "")
        notes = request.POST.get("notes", "")
        discount = float(request.POST.get("discount_summary", 0) or 0)

        # Convert date from MM/DD/YY to YYYY-MM-DD
        invoice_date = None
        if invoice_date_str:
            try:
                # Parse MM/DD/YY format
                date_obj = datetime.strptime(invoice_date_str, '%m/%d/%y')
                invoice_date = date_obj.date()
            except ValueError:
                try:
                    # Try MM/DD/YYYY format just in case
                    date_obj = datetime.strptime(invoice_date_str, '%m/%d/%Y')
                    invoice_date = date_obj.date()
                except ValueError:
                    # If all else fails, use today
                    invoice_date = timezone.now().date()
        else:
            invoice_date = timezone.now().date()
        
        # Get customer and agent
        customer_code = request.POST.get("customer_code")
        customer = None
        if customer_code:
            try:
                customer = Customer.objects.get(customer_id=customer_code)
            except Customer.DoesNotExist:
                pass
        
        sales_agent_id = request.POST.get("sales_agent")
        agent = None
        if sales_agent_id:
            try:
                agent = Agent.objects.get(agent_id=sales_agent_id)
            except Agent.DoesNotExist:
                pass
        
        # Calculate totals
        grand_total = float(request.POST.get("grand_total", 0) or 0)
        amount_due = float(request.POST.get("amount_due", 0) or 0)
        
        # Generate invoice number using the classmethod
        invoice_number = SalesInvoice._next_invoice_no()
        
        # Create invoice - using CORRECT field names
        invoice = SalesInvoice.objects.create(
            customer=customer,
            agent=agent,
            invoice_no=invoice_number,  # This is the display number
            date=invoice_date or timezone.now().date(),  # Field is 'date' not 'invoice_date'
            plate_no=plate_no,
            terms=terms,
            remarks=notes,  # Field is 'remarks' not 'notes'
            discount=discount,
            grand_total=grand_total,
            remaining_balance=amount_due,  # Field is 'remaining_balance' not 'balance'
            # payment_status will be set automatically by _recompute()
            # delivery_status defaults to False
        )
        
        # ===== SAVE ORDER RECORDS (ITEMS) =====
        i = 0
        while f"items[{i}][code]" in request.POST:
            code = request.POST.get(f"items[{i}][code]")
            desc = request.POST.get(f"items[{i}][desc]")
            quantity = int(request.POST.get(f"items[{i}][quantity]", 0) or 0)
            price = float(request.POST.get(f"items[{i}][price]", 0) or 0)
            rate = float(request.POST.get(f"items[{i}][rate]", 1) or 1)

            if code or desc:
                product = None
                if code:
                    try:
                        product = Product.objects.get(product_code=code)
                    except Product.DoesNotExist:
                        product = None

                # IMPORTANT: Only create if product exists (to avoid FK null issues if your model disallows null)
                if product:
                    OrderRecord.objects.create(
                        invoice=invoice,
                        product=product,
                        order_quantity=quantity,
                        order_price_per_unit=price,
                        rate=rate,
                    )
            i += 1

        # Recompute totals/status after creating records
        invoice.save()

        return redirect("main_page")
    
    # GET request - show empty form with auto-generated invoice number
    context = {
        "agents": Agent.objects.all().order_by("name"),
        "customers": Customer.objects.all().order_by("name"),
        "products": Product.objects.all(),
        "banks": Bank.objects.all(),
        "next_sales_invoice_no": SalesInvoice._next_invoice_no(),
        "today": timezone.now().date(),
        "is_deleted": False,
    }
    return render(request, "sales_invoice.html", context)

def sales_invoice_update(request, invoice_id):
    """Update an existing sales invoice"""
    invoice = get_object_or_404(SalesInvoice, invoice_no=invoice_id)
    
    if request.method == "POST":
        # Check if this is a delete request
        if request.POST.get("action_type") == "delete":
            invoice.is_deleted = True
            invoice.deleted_at = timezone.now()
            invoice.save(update_fields=["is_deleted", "deleted_at"])
            return redirect("main_page")
        
        # Don't allow editing deleted invoices
        if invoice.is_deleted:
            # Just redirect back to the view page
            return redirect("sales_invoice_update", invoice.invoice_no)
        
        # === PROCESS UPDATE ===
        # Get form data
        invoice_date_str = request.POST.get("invoice_date")
        plate_no = request.POST.get("plate_no", "")
        terms = request.POST.get("terms", "")
        notes = request.POST.get("notes", "")
        discount = float(request.POST.get("discount_summary", 0) or 0)
        
        # Convert date
        from datetime import datetime
        invoice_date = None
        if invoice_date_str:
            try:
                date_obj = datetime.strptime(invoice_date_str, '%Y-%m-%d')
                invoice_date = date_obj.date()
            except ValueError:
                invoice_date = timezone.now().date()
        else:
            invoice_date = timezone.now().date()
        
        # Get customer and agent
        customer_code = request.POST.get("customer_code")
        customer = None
        if customer_code:
            try:
                customer = Customer.objects.get(customer_id=customer_code)
            except Customer.DoesNotExist:
                pass
        
        sales_agent_id = request.POST.get("sales_agent")
        agent = None
        if sales_agent_id:
            try:
                agent = Agent.objects.get(agent_id=sales_agent_id)
            except Agent.DoesNotExist:
                pass
        
        # Update invoice fields
        invoice.customer = customer
        invoice.agent = agent
        invoice.date = invoice_date
        invoice.plate_no = plate_no
        invoice.terms = terms
        invoice.remarks = notes
        invoice.discount = discount
        
        # Delete existing related records
        invoice.order_records.all().delete()
        invoice.return_records.all().delete()
        invoice.payment_records.all().delete()
        
        # ===== SAVE ORDER RECORDS (ITEMS) =====
        i = 0
        while f"items[{i}][code]" in request.POST:
            code = request.POST.get(f"items[{i}][code]")
            desc = request.POST.get(f"items[{i}][desc]")
            quantity = int(request.POST.get(f"items[{i}][quantity]", 0) or 0)
            price = float(request.POST.get(f"items[{i}][price]", 0) or 0)
            rate = float(request.POST.get(f"items[{i}][rate]", 1) or 1)
            
            if code or desc:  # Only save if there's data
                # Find product
                product = None
                if code:
                    try:
                        product = Product.objects.get(product_code=code)
                    except Product.DoesNotExist:
                        pass
                
                # Create order record
                OrderRecord.objects.create(
                    invoice=invoice,
                    product=product,
                    order_quantity=quantity,
                    order_price_per_unit=price,
                    rate=rate,
                )
            i += 1
        
        # ===== SAVE RETURN RECORDS =====
        i = 0
        while f"returns[{i}][code]" in request.POST:
            code = request.POST.get(f"returns[{i}][code]")
            desc = request.POST.get(f"returns[{i}][desc]")
            quantity = int(request.POST.get(f"returns[{i}][quantity]", 0) or 0)
            price = float(request.POST.get(f"returns[{i}][price]", 0) or 0)
            rate = float(request.POST.get(f"returns[{i}][rate]", 1) or 1)
            
            if code or desc:
                product = None
                if code:
                    try:
                        product = Product.objects.get(product_code=code)
                    except Product.DoesNotExist:
                        pass
                
                ReturnRecord.objects.create(
                    invoice=invoice,
                    product=product,
                    return_quantity=quantity,
                    return_price_per_unit=price,
                    rate=rate,
                )
            i += 1
        
        # ===== SAVE PAYMENT RECORDS =====
        i = 0
        while f"payments[{i}][type]" in request.POST:
            payment_type = request.POST.get(f"payments[{i}][type]")
            bank_name = request.POST.get(f"payments[{i}][bank]", "")
            cheque_no = request.POST.get(f"payments[{i}][cheque_no]", "")
            amount = float(request.POST.get(f"payments[{i}][amount]", 0) or 0)
            payment_date_str = request.POST.get(f"payments[{i}][date]", "")
            status = request.POST.get(f"payments[{i}][status]", "valid")
            
            if amount > 0:
                # Parse payment date
                payment_date = None
                if payment_date_str:
                    try:
                        date_obj = datetime.strptime(payment_date_str, '%m/%d/%y')
                        payment_date = date_obj.date()
                    except ValueError:
                        payment_date = timezone.now().date()
                else:
                    payment_date = timezone.now().date()
                
                # Create payment record
                payment = PaymentRecord.objects.create(
                    invoice=invoice,
                    payment_date=payment_date,
                    amount=amount,
                    payment_type="Cash" if payment_type == "cash" else "Cheque",
                )
                
                # If cheque, create cheque payment record
                if payment_type == "cheque" and bank_name:
                    # Find bank
                    bank = None
                    try:
                        bank = Bank.objects.get(bank_acronym__icontains=bank_name)
                    except Bank.DoesNotExist:
                        pass
                    
                    ChequePayment.objects.create(
                        payment_record=payment,
                        bank=bank,
                        cq_date=payment_date,
                        cheque_no=cheque_no,
                        status=status.capitalize(),
                    )
            i += 1
        
        # Calculate totals and save invoice
        # The _recompute method will be called automatically when we save
        invoice.save()
        
        return redirect("main_page")
    
    # === DISPLAY FORM (GET request) ===
    context = {
        "invoice": invoice,
        "agents": Agent.objects.all().order_by("name"),
        "customers": Customer.objects.all().order_by("name"),
        "products": Product.objects.all(),
        "banks": Bank.objects.all(),
        "next_sales_invoice_no": invoice.invoice_no,
        "today": timezone.now().date(),
        "is_update": True,
        "is_deleted": invoice.is_deleted,
        # Make sure these are explicitly passed
        "order_records": invoice.order_records.all(),
        "return_records": invoice.return_records.all(),
        "payment_records": invoice.payment_records.all(),
    }
    return render(request, "sales_invoice.html", context)

def sales_invoice_print(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, invoice_no=invoice_id)
    context = {
        "invoice": invoice,
    }
    return render(request, "sales_invoice_print.html", context)


def sales_invoice_details(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, invoice_no=invoice_id)
    context = {
        "invoice": invoice,
    }
    return render(request, "sales_invoice_details.html", context)

from django.utils import timezone

def sales_invoice_delete(request, invoice_id):
    if request.method == "POST":
        invoice = get_object_or_404(SalesInvoice, invoice_no=invoice_id)
        invoice.is_deleted = True
        invoice.deleted_at = timezone.now()
        invoice.save(update_fields=["is_deleted", "deleted_at"])
    return redirect("main_page")