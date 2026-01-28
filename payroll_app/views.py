from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from payroll_app.models import Account, Product, Customer, Supplier, SalesInvoice, PurchaseInvoice, InvoiceItem, PurchaseInvoiceItem
from django.contrib import messages
from datetime import date
from django.db.models import Sum
from datetime import datetime

# Login
def home_redirect(request):
    message = request.session.pop('message', '')

    if request.method == 'POST':
        un = request.POST['username']
        pw = request.POST['password']
        try:
            user = Account.objects.get(username=un, password=pw)
            request.session['user_id'] = user.id
            return redirect('main_page')
        except Account.DoesNotExist:
            message = "Invalid login."
    if request.session.get('user_id'):
        return redirect('main_page')
    return render(request, 'login.html', {'message': message})

# Sign Up
def signup_view(request):
    if request.method == 'POST':
        un = request.POST['username']
        pw = request.POST['password']
        if Account.objects.filter(username=un).exists():
            message = "Account already exists."
            return render(request, 'signup.html', {'message': message})
        else:
            Account.objects.create(username=un, password=pw)
            request.session['message'] = "Account created successfully."
            return redirect('home')
    return render(request, 'signup.html')

# Manage Account
def manage_account(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if logout_view(request):
        return redirect('home')
    
    account = get_object_or_404(Account, pk=pk)

    return render(request, 'manage_account.html', {'account': account, 'user_id':user_id})

# Log Out
def logout_view(request):
    if 'logout' in request.GET:
        request.session.flush()
        return True
    return False

# Change Password
def change_password(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if logout_view(request):
        return redirect('home')
    
    account = get_object_or_404(Account, pk=pk)

    if request.method == 'POST':
        old_pw = request.POST.get('old_password')
        new_pw1 = request.POST.get('new_password1')
        new_pw2 = request.POST.get('new_password2')

        if old_pw != account.password:
            return render (request, 'change_password.html', {'user_id':user_id, 'error': 'Current password is incorrect.'})
        if new_pw1 != new_pw2:
            return render (request, 'change_password.html', {'user_id':user_id, 'error': 'New passwords do not match.'})
        
        account.password = new_pw1
        account.save()
        return redirect('manage_account', pk=pk)
            
    return render(request, 'change_password.html', {'account':account, 'user_id':user_id})

# Delete Account
def delete_account(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if logout_view(request):
        return redirect('home')
    
    account = get_object_or_404(Account, pk=pk)

    account.delete()
    request.session.pop('user_id', None)
    return redirect('home')

def main_page(request):
    active_tab = request.GET.get('tab', 'sales')

    # --- SALES LOGIC ---
    sales_qs = SalesInvoice.objects.all().order_by('-invoice_date')
    customers = Customer.objects.all()

    # Convert QuerySet into list of dicts (arrays)
    sales_invoices_list = [
        {
            'invoice_number': inv.invoice_number,
            'invoice_date': inv.invoice_date,
            'customer_id': inv.customer.id if inv.customer else None,
            'customer_name': inv.customer.company_name if inv.customer else 'N/A',
            'grand_total': float(inv.grand_total),
            'amount_due': float(inv.amount_due),
            'payment_amount': float(inv.payment_amount),
            'payment_type': inv.payment_type,
        }
        for inv in sales_qs
    ]

    # --- CREATE HASH TABLES FOR FAST LOOKUP ---
    # Keyed by customer_id
    sales_by_customer = {}
    for inv in sales_invoices_list:
        sales_by_customer.setdefault(inv['customer_id'], []).append(inv)

    # Keyed by invoice_number
    sales_by_invoice_number = {inv['invoice_number']: inv for inv in sales_invoices_list}

    filtered_sales = sales_invoices_list

    # --- Apply sales filters ---
    sales_invoice_number = request.GET.get('sales_invoice_number', '').strip()
    sales_customer = request.GET.get('sales_customer', '').strip()
    sales_start_date = request.GET.get('sales_start_date', '').strip()
    sales_end_date = request.GET.get('sales_end_date', '').strip()
    sales_payment_status = request.GET.get('sales_payment_status', '').strip()
    sales_payment_type = request.GET.get('sales_payment_type', '').strip()

     # Filter by invoice number (exact match)
    if sales_invoice_number:
        invoice = sales_by_invoice_number.get(sales_invoice_number)
        filtered_sales = [invoice] if invoice else []

    # Filter by customer (hash table lookup)
    if sales_customer:
        customer_id = int(sales_customer)
        filtered_sales = sales_by_customer.get(customer_id, [])

    # Other filters: date range, payment type/status
    if sales_start_date:
        start_date = datetime.fromisoformat(sales_start_date).date()
        filtered_sales = [inv for inv in filtered_sales if inv['invoice_date'] >= start_date]

    if sales_end_date:
        end_date = datetime.fromisoformat(sales_end_date).date()
        filtered_sales = [inv for inv in filtered_sales if inv['invoice_date'] <= end_date]

    if sales_payment_type:
        filtered_sales = [inv for inv in filtered_sales if inv['payment_type'] == sales_payment_type]

    # --- CALCULATE TOTALS ---
    total_sales = sum(inv['grand_total'] for inv in filtered_sales)
    total_sales_received = sum(inv['payment_amount'] for inv in filtered_sales)
    total_sales_due = sum(inv['amount_due'] for inv in filtered_sales)

    # --- PURCHASING LOGIC ---
    purchase_qs = PurchaseInvoice.objects.select_related('supplier').all().order_by('-invoice_date')
    suppliers = Supplier.objects.all()

    purchase_invoices_list = [
        {
            'invoice_number': inv.invoice_number,
            'invoice_date': inv.invoice_date,
            'supplier_id': inv.supplier.id,
            'supplier_name': inv.supplier.supplier_name,
            'invoice_total': float(inv.invoice_total),
            'amount_due': float(inv.amount_due),
            'payment_type': inv.payment_type,
        }
        for inv in purchase_qs
    ]

    # Hash table for supplier lookup
    purchase_by_supplier = {}
    for inv in purchase_invoices_list:
        purchase_by_supplier.setdefault(inv['supplier_id'], []).append(inv)

    # Apply filters (similar logic as sales)
    filtered_purchases = purchase_invoices_list

    purchase_invoice_number = request.GET.get('purchase_invoice_number', '').strip()
    supplier = request.GET.get('supplier', '').strip()
    purchase_start_date = request.GET.get('purchase_start_date', '').strip()
    purchase_end_date = request.GET.get('purchase_end_date', '').strip()
    purchase_payment_status = request.GET.get('purchase_payment_status', '').strip()
    purchase_payment_type = request.GET.get('purchase_payment_type', '').strip()

    if purchase_invoice_number:
        filtered_purchases = [inv for inv in filtered_purchases if purchase_invoice_number in inv['invoice_number']]

    if supplier:
        supplier_id = int(supplier)
        filtered_purchases = purchase_by_supplier.get(supplier_id, [])

    if purchase_start_date:
        start_date = datetime.fromisoformat(purchase_start_date).date()
        filtered_purchases = [inv for inv in filtered_purchases if inv['invoice_date'] >= start_date]

    if purchase_end_date:
        end_date = datetime.fromisoformat(purchase_end_date).date()
        filtered_purchases = [inv for inv in filtered_purchases if inv['invoice_date'] <= end_date]

    if purchase_payment_type:
        filtered_purchases = [inv for inv in filtered_purchases if inv['payment_type'] == purchase_payment_type]


    total_purchases = sum(inv['invoice_total'] for inv in filtered_purchases)
    total_purchases_due = sum(inv['amount_due'] for inv in filtered_purchases)
    total_purchases_paid = total_purchases - total_purchases_due

    context = {
        'sales_invoices': filtered_sales,
        'customers': customers,
        'total_sales': total_sales,
        'total_sales_received': total_sales_received,
        'total_sales_due': total_sales_due,

        'purchase_invoices': filtered_purchases,
        'suppliers': suppliers,
        'total_purchases': total_purchases,
        'total_purchases_paid': total_purchases_paid,
        'total_purchases_due': total_purchases_due,

        'active_tab': active_tab,
        'request': request,
    }

    return render(request, 'main_page.html', context)

def create_invoice(request):
    customers = Customer.objects.all()
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    
    # Generate next sales invoice number
    current_year = date.today().strftime('%y')
    
    # Sales invoice number
    last_sales_invoice = SalesInvoice.objects.filter(
        invoice_number__startswith=f"{current_year}OF"
    ).order_by('-invoice_number').first()
    
    if last_sales_invoice:
        try:
            last_number = int(last_sales_invoice.invoice_number[4:])
            next_sales_number = last_number + 1
            next_sales_invoice_number = f"{current_year}OF{next_sales_number:06d}"
        except (ValueError, IndexError):
            next_sales_invoice_number = f"{current_year}OF000001"
    else:
        next_sales_invoice_number = f"{current_year}OF000001"
    
    # Purchase invoice number
    last_purchase_invoice = PurchaseInvoice.objects.filter(
        invoice_number__startswith=f"{current_year}PO"
    ).order_by('-invoice_number').first()
    
    if last_purchase_invoice:
        try:
            last_number = int(last_purchase_invoice.invoice_number[4:])
            next_purchase_number = last_number + 1
            next_purchase_invoice_number = f"{current_year}PO{next_purchase_number:06d}"
        except (ValueError, IndexError):
            next_purchase_invoice_number = f"{current_year}PO000001"
    else:
        next_purchase_invoice_number = f"{current_year}PO000001"
    
    # Check if loading existing invoice
    load_invoice = request.GET.get('load')
    invoice_data = None
    is_update = False
    
    if load_invoice:
        try:
            # Try sales invoice first
            invoice = SalesInvoice.objects.get(invoice_number=load_invoice)
            is_update = True
            invoice_data = {
                'type': 'sales',
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
                'plate_no': invoice.plate_no or '',
                'customer_id': invoice.customer.id,
                'payment_type': invoice.payment_type,
                'discount': float(invoice.discount),
                'payment_amount': float(invoice.payment_amount),
                'discount_received': invoice.discount_received,
                'items': [
                    {
                        'code': item.product_code,
                        'desc': item.description,
                        'quantity': item.quantity,
                        'unit': item.unit,
                        'price': float(item.price),
                        'rate': float(item.rate),
                        'amount': float(item.amount)
                    }
                    for item in invoice.items.all()
                ]
            }
        except SalesInvoice.DoesNotExist:
            try:
                # Try purchase invoice
                invoice = PurchaseInvoice.objects.get(invoice_number=load_invoice)
                is_update = True
                invoice_data = {
                    'type': 'purchase',
                    'id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
                    'supplier_id': invoice.supplier.id,
                    'payment_type': invoice.payment_type,
                    'discount': float(invoice.discount),
                    'items': [
                        {
                            'code': item.product_code,
                            'desc': item.description,
                            'quantity': item.quantity,
                            'unit': item.unit,
                            'price': float(item.price),
                            'rate': float(item.rate),
                            'amount': float(item.amount)
                        }
                        for item in invoice.items.all()
                    ]
                }
            except PurchaseInvoice.DoesNotExist:
                messages.error(request, f'Invoice {load_invoice} not found.')
    
    # Determine active tab
    active_tab = request.GET.get('tab', 'sales')
    if invoice_data and invoice_data['type']:
        active_tab = invoice_data['type']
    
    context = {
        'customers': customers,
        'suppliers': suppliers,
        'products': products,
        'next_sales_invoice_number': next_sales_invoice_number,
        'next_purchase_invoice_number': next_purchase_invoice_number,
        'current_date': date.today(),
        'active_tab': active_tab,
        'invoice_data': invoice_data,
        'is_update': is_update,
    }
    return render(request, 'create_invoice.html', context)

def sales_invoice_create(request):
    if request.method == 'POST':
        try:
            print("=== DEBUG: Starting sales_invoice_create ===")
            print("POST data:", dict(request.POST))
            
            # Get basic form data
            invoice_number = request.POST.get('invoice_number')
            invoice_date = request.POST.get('invoice_date')
            customer_id = request.POST.get('customer')
            payment_type = request.POST.get('payment_type', 'cash')
            discount = float(request.POST.get('discount', 0))
            subtotal = float(request.POST.get('subtotal', 0))
            grand_total = float(request.POST.get('grand_total', 0))
            
            print(f"Invoice: {invoice_number}, Date: {invoice_date}, Customer: {customer_id}")
            print(f"Payment: {payment_type}, Discount: {discount}, Subtotal: {subtotal}, Grand Total: {grand_total}")
            
            # Get customer
            customer = Customer.objects.get(id=customer_id)
            
            # Create the invoice with simplified fields
            invoice = SalesInvoice(
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                customer=customer,
                payment_type=payment_type,
                discount=discount,
                invoice_total=subtotal,
                grand_total=grand_total,
                amount_due=0,  # Since everything is paid
                payment_amount=grand_total,  # Payment equals grand total
            )
            invoice.save()
            print(f"=== DEBUG: Invoice saved with ID: {invoice.id} ===")
            
            # Save invoice items
            item_count = 0
            while f'items[{item_count}][code]' in request.POST:
                product_code = request.POST.get(f'items[{item_count}][code]')
                if product_code:
                    # Try to get the product by code, or use the form data
                    try:
                        product = Product.objects.get(product_code=product_code)
                        description = product.description
                        unit = product.unit
                    except Product.DoesNotExist:
                        # Fallback to form data if product not found
                        description = request.POST.get(f'items[{item_count}][desc]', '')
                        unit = request.POST.get(f'items[{item_count}][unit]', 'PCS')
                    
                    quantity = int(request.POST.get(f'items[{item_count}][quantity]', 1))
                    price = float(request.POST.get(f'items[{item_count}][price]', 0))
                    amount = float(request.POST.get(f'items[{item_count}][amount]', 0))
                    
                    print(f"Item {item_count}: {product_code}, Qty: {quantity}, Price: {price}, Amount: {amount}")
                    
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product_code=product_code,
                        description=description,
                        quantity=quantity,
                        unit=unit,
                        price=price,
                        amount=amount
                    )
                item_count += 1
            
            print(f"=== DEBUG: Saved {item_count} items ===")
            messages.success(request, f'Invoice {invoice_number} created successfully!')
            return redirect('main_page')
                
        except Exception as e:
            print(f"=== DEBUG: Exception occurred: {str(e)} ===")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f'Error creating invoice: {str(e)}')
            return redirect('create_invoice')
    
    return redirect('create_invoice')

def purchase_invoice_create(request):
    if request.method == 'POST':
        try:
            invoice_number = request.POST.get('invoice_number')
            invoice_date = request.POST.get('invoice_date')
            supplier_id = request.POST.get('supplier')
            payment_type = request.POST.get('payment_type', 'cash')
            discount = float(request.POST.get('discount', 0))
            
            supplier = Supplier.objects.get(id=supplier_id)
            
            # Create purchase invoice - REMOVED all bank/cheque fields
            invoice = PurchaseInvoice(
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                supplier=supplier,
                payment_type=payment_type,
                discount=discount,
            )
            
            # Calculate totals from items
            invoice_total = 0
            item_count = 0
            
            # Process items
            while f'items[{item_count}][code]' in request.POST:
                code = request.POST.get(f'items[{item_count}][code]')
                if code:  # Only process if product code is provided
                    desc = request.POST.get(f'items[{item_count}][desc]', '')
                    quantity = int(request.POST.get(f'items[{item_count}][quantity]', 1))
                    unit = request.POST.get(f'items[{item_count}][unit]', 'PCS')
                    price = float(request.POST.get(f'items[{item_count}][price]', 0))
                    rate = float(request.POST.get(f'items[{item_count}][rate]', 1))
                    amount = quantity * price * rate
                    
                    invoice_total += amount
                item_count += 1
            
            # Set totals - Since everything is paid, amount_due is 0
            invoice.invoice_total = invoice_total
            invoice.grand_total = invoice_total - discount
            invoice.amount_due = 0  # Always 0 since everything is paid
            
            # Save invoice
            invoice.save()
            
            # Now save the items with the invoice instance
            item_count = 0
            while f'items[{item_count}][code]' in request.POST:
                code = request.POST.get(f'items[{item_count}][code]')
                if code:
                    desc = request.POST.get(f'items[{item_count}][desc]', '')
                    quantity = int(request.POST.get(f'items[{item_count}][quantity]', 1))
                    unit = request.POST.get(f'items[{item_count}][unit]', 'PCS')
                    price = float(request.POST.get(f'items[{item_count}][price]', 0))
                    rate = float(request.POST.get(f'items[{item_count}][rate]', 1))
                    amount = quantity * price * rate
                    
                    PurchaseInvoiceItem.objects.create(
                        invoice=invoice,
                        product_code=code,
                        description=desc,
                        quantity=quantity,
                        unit=unit,
                        price=price,
                        rate=rate,
                        amount=amount
                    )
                item_count += 1
            
            action = request.POST.get('action')
            if action == 'save_print':
                return redirect('purchase_invoice_print', pk=invoice.id)
            else:
                messages.success(request, f'Purchase Invoice {invoice_number} created successfully!')
                return redirect('main_page')
                
        except Exception as e:
            messages.error(request, f'Error creating purchase invoice: {str(e)}')
            return redirect('create_invoice')
    
    return redirect('create_invoice')

def sales_invoice_print(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)
    
    # Get invoice items
    try:
        items = invoice.items.all()
    except:
        items = []
    
    context = {
        'invoice': invoice,
        'items': items,
    }
    return render(request, 'sales_invoice_print.html', context)

def purchase_invoice_print(request, invoice_id):
    invoice = get_object_or_404(PurchaseInvoice, id=invoice_id)
    
    # Get invoice items
    try:
        items = invoice.items.all()
    except:
        items = []
    
    context = {
        'invoice': invoice,
        'items': items,
    }
    return render(request, 'purchase_invoice_print.html', context)

def binary_search(arr, target, key):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_value = key(arr[mid])
        if mid_value == target:
            return arr[mid]
        elif mid_value < target:
            low = mid + 1
        else:
            high = mid - 1
    return None

def merge_sort(arr, key=lambda x: x):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    return merge(left, right, key)

def merge(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def profiles(request):
    active_tab = request.GET.get('tab', 'product')

    products_qs = Product.objects.all()
    
    # Get filter inputs
    product_code = request.GET.get('product_code', '').strip().lower()
    description = request.GET.get('description', '').strip().lower()
    
    # Filter by description first (optional: can keep ORM filter)
    if description:
        products_qs = products_qs.filter(description__icontains=description)
    
    # Convert queryset to list
    products_list = list(products_qs)
    
    # Sort products by product_code using merge_sort
    products_list = merge_sort(products_list, key=lambda p: p.product_code.lower())
    
    # Apply binary search if a product_code is provided
    if product_code:
        result = binary_search(products_list, product_code, key=lambda p: p.product_code.lower())
        products = [result] if result else []
    else:
        products = products_list
    
    # Generate next product code
    last_product = Product.objects.order_by('-id').first()
    next_product_code = "P001"
    if last_product:
        try:
            last_code = last_product.product_code
            if last_code.startswith('P'):
                number_part = last_code[1:]
                next_number = int(number_part) + 1
                next_product_code = f"P{next_number:03d}"
        except (ValueError, IndexError):
            pass
    
    # CUSTOMER LOGIC
    customers = Customer.objects.all().order_by('customer_code')
    
    # Apply customer filters
    customer_code = request.GET.get('customer_code', '')
    company_name = request.GET.get('company_name', '')
    contact_person = request.GET.get('contact_person', '')
    phone = request.GET.get('phone', '')
    area = request.GET.get('area', '')
    customer_address = request.GET.get('customer_address', '')
    
    if customer_code:
        customers = customers.filter(customer_code__icontains=customer_code)
    
    if company_name:
        customers = customers.filter(company_name__icontains=company_name)
    
    if contact_person:
        customers = customers.filter(contact_person__icontains=contact_person)
    
    if phone:
        customers = customers.filter(phone__icontains=phone)
    
    if area:
        customers = customers.filter(area__icontains=area)
    
    if customer_address:
        customers = customers.filter(customer_address__icontains=customer_address)
    
    # Generate next customer code
    last_customer = Customer.objects.order_by('-id').first()
    next_customer_code = "C001"
    
    if last_customer:
        try:
            last_code = last_customer.customer_code
            if last_code.startswith('C'):
                number_part = last_code[1:]
                next_number = int(number_part) + 1
                next_customer_code = f"C{next_number:03d}"
        except (ValueError, IndexError):
            pass
    
    # SUPPLIER LOGIC
    suppliers = Supplier.objects.all().order_by('supplier_code')
    
    # Apply supplier filters
    supplier_code = request.GET.get('supplier_code', '')
    supplier_name = request.GET.get('supplier_name', '')
    supplier_contact_person = request.GET.get('supplier_contact_person', '')
    supplier_phone = request.GET.get('supplier_phone', '')
    supplier_area = request.GET.get('supplier_area', '')
    supplier_address = request.GET.get('supplier_address', '')
    
    if supplier_code:
        suppliers = suppliers.filter(supplier_code__icontains=supplier_code)
    
    if supplier_name:
        suppliers = suppliers.filter(supplier_name__icontains=supplier_name)
    
    if supplier_contact_person:
        suppliers = suppliers.filter(contact_person__icontains=supplier_contact_person)
    
    if supplier_phone:
        suppliers = suppliers.filter(phone__icontains=supplier_phone)
    
    if supplier_area:
        suppliers = suppliers.filter(area__icontains=supplier_area)
    
    if supplier_address:
        suppliers = suppliers.filter(supplier_address__icontains=supplier_address)
    
    # Generate next supplier code
    last_supplier = Supplier.objects.order_by('-id').first()
    next_supplier_code = "S001"
    
    if last_supplier:
        try:
            last_code = last_supplier.supplier_code
            if last_code.startswith('S'):
                number_part = last_code[1:]
                next_number = int(number_part) + 1
                next_supplier_code = f"S{next_number:03d}"
        except (ValueError, IndexError):
            pass
    
    context = {
        # Products
        'products': products,
        'next_product_code': next_product_code,
        
        # Customers
        'customers': customers,
        'next_customer_code': next_customer_code,
        
        # Suppliers
        'suppliers': suppliers,
        'next_supplier_code': next_supplier_code,
        
        # Active tab
        'active_tab': active_tab,
        'request': request,
    }
    return render(request, 'profiles.html', context)

def product_create(request):
    if request.method == 'POST':
        try:
            product_code = request.POST.get('product_code')
            description = request.POST.get('description')
            price = float(request.POST.get('price', 0))
            unit = request.POST.get('unit', 'PCS')
            
            # Check if product code already exists
            if Product.objects.filter(product_code=product_code).exists():
                messages.error(request, f'Product code {product_code} already exists!')
            else:
                product = Product(
                    product_code=product_code,
                    description=description,
                    price=price,
                    unit=unit
                )
                product.save()
                messages.success(request, f'Product {description} created successfully!')
                
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
    
    return redirect('profiles')

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            product.product_code = request.POST.get('product_code')
            product.description = request.POST.get('description')
            product.price = float(request.POST.get('price', 0))
            product.unit = request.POST.get('unit', 'PCS')
            product.save()
            
            messages.success(request, f'Product {product.description} updated successfully!')
            return redirect('profiles')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    return render(request, 'product_form.html', {'product': product})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    description = product.description
    
    try:
        product.delete()
        messages.success(request, f'Product {description} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting product: {str(e)}')
    
    return redirect('profiles')

def customer_create(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            try:
                customer_code = request.POST.get('customer_code')
                company_name = request.POST.get('company_name')
                contact_person = request.POST.get('contact_person')
                customer_address = request.POST.get('customer_address', '')
                phone = request.POST.get('phone', '')
                area = request.POST.get('area', '')
                
                # Check if customer code already exists
                if Customer.objects.filter(customer_code=customer_code).exists():
                    messages.error(request, f'Customer code {customer_code} already exists!')
                else:
                    customer = Customer(
                        customer_code=customer_code,
                        company_name=company_name,
                        contact_person=contact_person,
                        customer_address=customer_address,
                        phone=phone,
                        area=area
                    )
                    customer.save()
                    messages.success(request, f'Customer {company_name} created successfully!')
                    
            except Exception as e:
                messages.error(request, f'Error creating customer: {str(e)}')
        
        # For search action, it will be handled by the profiles view
        elif action == 'search':
            pass  # Search is handled by GET parameters in profiles view
    
    # Get the active tab to redirect back to the correct tab
    active_tab = request.POST.get('tab', 'customer')
    return redirect(f'{profiles}?tab={active_tab}')

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        try:
            customer.customer_code = request.POST.get('customer_code')
            customer.company_name = request.POST.get('company_name')
            customer.contact_person = request.POST.get('contact_person')
            customer.customer_address = request.POST.get('customer_address', '')
            customer.phone = request.POST.get('phone', '')
            customer.area = request.POST.get('area', '')
            customer.save()
            
            messages.success(request, f'Customer {customer.company_name} updated successfully!')
            return redirect('profiles')
            
        except Exception as e:
            messages.error(request, f'Error updating customer: {str(e)}')
    
    # If GET request, render the update form
    return render(request, 'customer_form.html', {'customer': customer})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    company_name = customer.company_name
    
    try:
        customer.delete()
        messages.success(request, f'Customer {company_name} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting customer: {str(e)}')
    
    active_tab = request.POST.get('tab', 'customer')
    return redirect(f'/profiles/?tab={active_tab}')

def supplier_create(request):
    if request.method == 'POST':
        try:
            supplier_code = request.POST.get('supplier_code')
            supplier_name = request.POST.get('supplier_name')
            contact_person = request.POST.get('contact_person')
            supplier_address = request.POST.get('supplier_address', '')
            phone = request.POST.get('phone', '')
            area = request.POST.get('area', '')
            
            # Check if supplier code already exists
            if Supplier.objects.filter(supplier_code=supplier_code).exists():
                messages.error(request, f'Supplier code {supplier_code} already exists!')
            else:
                supplier = Supplier(
                    supplier_code=supplier_code,
                    supplier_name=supplier_name,
                    contact_person=contact_person,
                    supplier_address=supplier_address,
                    phone=phone,
                    area=area
                )
                supplier.save()
                messages.success(request, f'Supplier {supplier_name} created successfully!')
                
        except Exception as e:
            messages.error(request, f'Error creating supplier: {str(e)}')
    
    active_tab = request.POST.get('tab', 'supplier')
    return redirect(f'/profiles/?tab={active_tab}')

def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        try:
            supplier.supplier_code = request.POST.get('supplier_code')
            supplier.supplier_name = request.POST.get('supplier_name')
            supplier.contact_person = request.POST.get('contact_person')
            supplier.supplier_address = request.POST.get('supplier_address', '')
            supplier.phone = request.POST.get('phone', '')
            supplier.area = request.POST.get('area', '')
            supplier.save()
            
            messages.success(request, f'Supplier {supplier.supplier_name} updated successfully!')
            return redirect('profiles')
            
        except Exception as e:
            messages.error(request, f'Error updating supplier: {str(e)}')
    
    return render(request, 'supplier_form.html', {'supplier': supplier})

def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier_name = supplier.supplier_name
    
    try:
        supplier.delete()
        messages.success(request, f'Supplier {supplier_name} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting supplier: {str(e)}')
    
    active_tab = request.POST.get('tab', 'supplier')
    return redirect(f'/profiles/?tab={active_tab}')