from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from payroll_app.models import (
    Account, Product, Customer, Agent, Bank,
    Sales_Transaction, Order_Record, Payment_Record, 
    Cheque_Payment, Return_Record
)
from django.contrib import messages
from datetime import date
from django.db.models import Sum, Q
from datetime import datetime
from django.core.validators import ValidationError

# Helper function to generate next ID
def generate_next_id(model_class, id_field, length):
    """Generate next ID as zero-padded number of specified length"""
    last_record = model_class.objects.order_by('-{}'.format(id_field)).first()
    
    if last_record:
        last_id = getattr(last_record, id_field)
        try:
            next_number = int(last_id) + 1
            next_id = f"{next_number:0{length}d}"
            return next_id
        except (ValueError, IndexError):
            return f"{1:0{length}d}"
    else:
        return f"{1:0{length}d}"

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

    return render(request, 'manage_account.html', {'account': account, 'user_id': user_id})

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
            return render(request, 'change_password.html', {'user_id': user_id, 'error': 'Current password is incorrect.'})
        if new_pw1 != new_pw2:
            return render(request, 'change_password.html', {'user_id': user_id, 'error': 'New passwords do not match.'})
        
        account.password = new_pw1
        account.save()
        return redirect('manage_account', pk=pk)
            
    return render(request, 'change_password.html', {'account': account, 'user_id': user_id})

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
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if logout_view(request):
        return redirect('home')
    
    active_tab = request.GET.get('tab', 'sales')

    # --- SALES LOGIC ---
    sales_qs = Sales_Transaction.objects.all().order_by('-date')
    customers = Customer.objects.all()
    agents = Agent.objects.all()

    # Convert QuerySet into list of dicts
    sales_invoices_list = [
        {
            'invoice_id': inv.invoice_id,
            'invoice_no': inv.invoice_no,
            'date': inv.date.strftime('%Y-%m-%d'),
            'customer_id': inv.customer.customer_id,
            'customer_name': inv.customer.name,
            'agent_name': inv.agent.name if inv.agent else 'N/A',
            'grand_total': float(inv.grand_total),
            'partial_payment': float(inv.partial_payment or 0),
            'remaining_balance': float(inv.remaining_balance),
            'payment_status': inv.payment_status,
            'delivery_status': inv.delivery_status,
            'discount': float(inv.discount or 0),
            'terms': inv.terms or '',
            'remarks': inv.remarks or '',
        }
        for inv in sales_qs
    ]

    # Create hash tables for fast lookup
    sales_by_customer = {}
    sales_by_invoice_no = {}
    for inv in sales_invoices_list:
        sales_by_customer.setdefault(inv['customer_id'], []).append(inv)
        sales_by_invoice_no[inv['invoice_no']] = inv

    filtered_sales = sales_invoices_list

    # Apply sales filters
    sales_invoice_no = request.GET.get('sales_invoice_no', '').strip()
    sales_customer = request.GET.get('sales_customer', '').strip()
    sales_start_date = request.GET.get('sales_start_date', '').strip()
    sales_end_date = request.GET.get('sales_end_date', '').strip()
    sales_payment_status = request.GET.get('sales_payment_status', '').strip()
    sales_delivery_status = request.GET.get('sales_delivery_status', '').strip()

    # Filter by invoice number (exact match)
    if sales_invoice_no:
        invoice = sales_by_invoice_no.get(sales_invoice_no)
        filtered_sales = [invoice] if invoice else []

    # Filter by customer
    if sales_customer:
        filtered_sales = sales_by_customer.get(sales_customer, [])

    # Date range filters
    if sales_start_date:
        start_date = datetime.strptime(sales_start_date, '%Y-%m-%d').date()
        filtered_sales = [inv for inv in filtered_sales if datetime.strptime(inv['date'], '%Y-%m-%d').date() >= start_date]

    if sales_end_date:
        end_date = datetime.strptime(sales_end_date, '%Y-%m-%d').date()
        filtered_sales = [inv for inv in filtered_sales if datetime.strptime(inv['date'], '%Y-%m-%d').date() <= end_date]

    # Payment status filter
    if sales_payment_status:
        filtered_sales = [inv for inv in filtered_sales if inv['payment_status'] == sales_payment_status]

    # Delivery status filter
    if sales_delivery_status:
        delivery_bool = sales_delivery_status.lower() == 'delivered'
        filtered_sales = [inv for inv in filtered_sales if inv['delivery_status'] == delivery_bool]

    # Calculate totals
    total_sales = sum(inv['grand_total'] for inv in filtered_sales)
    total_sales_received = sum(inv['partial_payment'] for inv in filtered_sales)
    total_sales_due = sum(inv['remaining_balance'] for inv in filtered_sales)

    # Get statistics for all sales (unfiltered)
    all_sales = sales_invoices_list
    total_all_sales = sum(inv['grand_total'] for inv in all_sales)
    total_all_received = sum(inv['partial_payment'] for inv in all_sales)
    total_all_due = sum(inv['remaining_balance'] for inv in all_sales)

    context = {
        'sales_invoices': filtered_sales,
        'customers': customers,
        'agents': agents,
        'total_sales': total_sales,
        'total_sales_received': total_sales_received,
        'total_sales_due': total_sales_due,
        'total_all_sales': total_all_sales,
        'total_all_received': total_all_received,
        'total_all_due': total_all_due,
        'active_tab': active_tab,
        'request': request,
        'user_id': user_id,
    }

    return render(request, 'main_page.html', context)

def create_invoice(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if logout_view(request):
        return redirect('home')
    
    customers = Customer.objects.all()
    agents = Agent.objects.all()
    products = Product.objects.filter(status='Active')
    banks = Bank.objects.all()
    
    # Generate next invoice number (format: YYOF######)
    current_year = date.today().strftime('%y')
    
    last_sales_invoice = Sales_Transaction.objects.filter(
        invoice_no__startswith=f"{current_year}OF"
    ).order_by('-invoice_no').first()
    
    if last_sales_invoice:
        try:
            last_number = int(last_sales_invoice.invoice_no[4:])  # Remove YYOF
            next_sales_number = last_number + 1
            next_sales_invoice_no = f"{current_year}OF{next_sales_number:06d}"
        except (ValueError, IndexError):
            next_sales_invoice_no = f"{current_year}OF000001"
    else:
        next_sales_invoice_no = f"{current_year}OF000001"
    
    # Generate next invoice ID (format: ########)
    next_invoice_id = generate_next_id(Sales_Transaction, 'invoice_id', '', 8)
    
    # Check if loading existing invoice
    load_invoice = request.GET.get('load')
    invoice_data = None
    is_update = False
    
    if load_invoice:
        try:
            invoice = Sales_Transaction.objects.get(invoice_no=load_invoice)
            is_update = True
            
            # Get order records
            order_items = []
            for order in invoice.order_records.all():
                order_items.append({
                    'product_id': order.product.product_id,
                    'product_code': order.product.product_code,
                    'description': order.product.description,
                    'order_quantity': order.order_quantity,
                    'order_price_per_unit': float(order.order_price_per_unit),
                    'rate': float(order.rate),
                    'total_price': float(order.total_price)
                })
            
            # Get return records
            return_items = []
            for ret in invoice.return_records.all():
                return_items.append({
                    'product_id': ret.product.product_id,
                    'product_code': ret.product.product_code,
                    'description': ret.product.description,
                    'return_quantity': ret.return_quantity,
                    'return_price_per_unit': float(ret.return_price_per_unit),
                    'rate': float(ret.rate),
                    'total_price': float(ret.total_price)
                })
            
            # Get payment records
            payments = []
            for payment in invoice.payment_records.all():
                payment_data = {
                    'payment_record_no': payment.payment_record_no,
                    'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                    'amount': float(payment.amount),
                    'payment_type': payment.payment_type,
                    'days': payment.days,
                }
                
                # Get cheque details if applicable
                if payment.payment_type == 'Cheque':
                    try:
                        cheque = Cheque_Payment.objects.get(
                            cq_invoice=invoice,
                            cq_payment_record_no=payment.payment_record_no
                        )
                        payment_data['bank_id'] = cheque.bank.bank_id if cheque.bank else None
                        payment_data['bank_name'] = cheque.bank.name if cheque.bank else ''
                        payment_data['cheque_no'] = cheque.cheque_no
                        payment_data['cq_date'] = cheque.cq_date.strftime('%Y-%m-%d')
                        payment_data['cheque_status'] = cheque.status
                    except Cheque_Payment.DoesNotExist:
                        pass
                
                payments.append(payment_data)
            
            invoice_data = {
                'invoice_id': invoice.invoice_id,
                'invoice_no': invoice.invoice_no,
                'date': invoice.date.strftime('%Y-%m-%d'),
                'customer_id': invoice.customer.customer_id,
                'agent_id': invoice.agent.agent_id if invoice.agent else None,
                'plate_no': invoice.plate_no or '',
                'terms': invoice.terms or '',
                'remarks': invoice.remarks or '',
                'delivery_status': invoice.delivery_status,
                'discount': float(invoice.discount or 0),
                'order_items': order_items,
                'return_items': return_items,
                'payments': payments,
                'grand_total': float(invoice.grand_total),
                'partial_payment': float(invoice.partial_payment or 0),
                'remaining_balance': float(invoice.remaining_balance),
                'payment_status': invoice.payment_status,
            }
            
        except Sales_Transaction.DoesNotExist:
            messages.error(request, f'Invoice {load_invoice} not found.')
    
    # Determine active tab
    active_tab = request.GET.get('tab', 'sales')
    
    context = {
        'customers': customers,
        'agents': agents,
        'products': products,
        'banks': banks,
        'next_sales_invoice_no': next_sales_invoice_no,
        'next_invoice_id': next_invoice_id,
        'current_date': date.today().strftime('%Y-%m-%d'),
        'active_tab': active_tab,
        'invoice_data': invoice_data,
        'is_update': is_update,
        'user_id': user_id,
    }
    return render(request, 'create_invoice.html', context)

def sales_invoice_create(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Get basic form data
            invoice_id = request.POST.get('invoice_id')
            invoice_no = request.POST.get('invoice_no')
            invoice_date = request.POST.get('invoice_date')
            customer_id = request.POST.get('customer')
            agent_id = request.POST.get('agent')
            plate_no = request.POST.get('plate_no', '')
            terms = request.POST.get('terms', '')
            remarks = request.POST.get('remarks', '')
            delivery_status = request.POST.get('delivery_status') == 'on'
            discount = float(request.POST.get('discount', 0) or 0)
            
            # Get customer and agent
            customer = Customer.objects.get(customer_id=customer_id)
            agent = None
            if agent_id:
                try:
                    agent = Agent.objects.get(agent_id=agent_id)
                except Agent.DoesNotExist:
                    pass
            
            # Calculate grand total from items
            total_order_amount = 0
            total_return_amount = 0
            
            # Calculate order totals
            item_count = 0
            while f'items[{item_count}][product_id]' in request.POST or f'items[{item_count}][code]' in request.POST:
                product_id = request.POST.get(f'items[{item_count}][product_id]')
                if product_id:
                    order_quantity = int(request.POST.get(f'items[{item_count}][quantity]', 0))
                    order_price = float(request.POST.get(f'items[{item_count}][price]', 0))
                    rate = float(request.POST.get(f'items[{item_count}][rate]', 1))
                    
                    total_order_amount += order_quantity * order_price * rate
                item_count += 1
            
            # Calculate return totals (if any)
            return_count = 0
            while f'return_items[{return_count}][product_id]' in request.POST:
                product_id = request.POST.get(f'return_items[{return_count}][product_id]')
                if product_id:
                    return_quantity = int(request.POST.get(f'return_items[{return_count}][quantity]', 0))
                    return_price = float(request.POST.get(f'return_items[{return_count}][price]', 0))
                    return_rate = float(request.POST.get(f'return_items[{return_count}][rate]', 1))
                    
                    total_return_amount += return_quantity * return_price * return_rate
                return_count += 1
            
            grand_total = total_order_amount - total_return_amount - discount
            
            # Create the sales transaction
            invoice = Sales_Transaction(
                invoice_id=invoice_id,
                invoice_no=invoice_no,
                date=invoice_date,
                customer=customer,
                agent=agent,
                plate_no=plate_no,
                terms=terms,
                remarks=remarks,
                delivery_status=delivery_status,
                discount=discount,
                grand_total=grand_total,
                partial_payment=0,
                remaining_balance=grand_total,
            )
            invoice.save()
            
            # Save order records
            item_count = 0
            while f'items[{item_count}][product_id]' in request.POST or f'items[{item_count}][code]' in request.POST:
                product_id = request.POST.get(f'items[{item_count}][product_id]')
                
                if product_id:
                    product = Product.objects.get(product_id=product_id)
                    
                    order_quantity = int(request.POST.get(f'items[{item_count}][quantity]', 0))
                    order_price = float(request.POST.get(f'items[{item_count}][price]', 0))
                    rate = float(request.POST.get(f'items[{item_count}][rate]', 1))
                    
                    if order_quantity > 0:
                        Order_Record.objects.create(
                            invoice=invoice,
                            product=product,
                            order_quantity=order_quantity,
                            order_price_per_unit=order_price,
                            rate=rate
                        )
                        
                        # Update product quantity (reduce stock)
                        product.quantity -= order_quantity
                        product.save()
                        
                item_count += 1
            
            # Save return records (if any)
            return_count = 0
            while f'return_items[{return_count}][product_id]' in request.POST:
                product_id = request.POST.get(f'return_items[{return_count}][product_id]')
                
                if product_id:
                    product = Product.objects.get(product_id=product_id)
                    
                    return_quantity = int(request.POST.get(f'return_items[{return_count}][quantity]', 0))
                    return_price = float(request.POST.get(f'return_items[{return_count}][price]', 0))
                    return_rate = float(request.POST.get(f'return_items[{return_count}][rate]', 1))
                    
                    if return_quantity > 0:
                        Return_Record.objects.create(
                            invoice=invoice,
                            product=product,
                            return_quantity=return_quantity,
                            return_price_per_unit=return_price,
                            rate=return_rate
                        )
                        
                        # Update product quantity (increase stock due to return)
                        product.quantity += return_quantity
                        product.save()
                        
                return_count += 1
            
            # Process payment if provided
            payment_amount = request.POST.get('payment_amount')
            if payment_amount and float(payment_amount) > 0:
                payment_type = request.POST.get('payment_type', 'Cash')
                
                # Generate payment record number
                next_payment_no = generate_next_id(Payment_Record, 'payment_record_no', '', 4)
                
                # Create payment record
                payment = Payment_Record.objects.create(
                    invoice=invoice,
                    payment_record_no=next_payment_no,
                    payment_date=date.today(),
                    amount=float(payment_amount),
                    payment_type=payment_type
                )
                
                # If cheque payment, create cheque record
                if payment_type == 'Cheque':
                    bank_id = request.POST.get('bank')
                    cheque_no = request.POST.get('cheque_no')
                    cq_date = request.POST.get('cq_date')
                    
                    if bank_id and cheque_no and cq_date:
                        bank = Bank.objects.get(bank_id=bank_id)
                        Cheque_Payment.objects.create(
                            cq_invoice=invoice,
                            cq_payment_record_no=next_payment_no,
                            bank=bank,
                            cq_date=cq_date,
                            cheque_no=cheque_no,
                            status='Valid'
                        )
            
            messages.success(request, f'Invoice {invoice_no} created successfully!')
            
            # Check if we should print
            if request.POST.get('action') == 'save_print':
                return redirect('sales_invoice_print', invoice_id=invoice.invoice_id)
            else:
                return redirect('main_page')
                
        except Exception as e:
            messages.error(request, f'Error creating invoice: {str(e)}')
            return redirect('create_invoice')
    
    return redirect('create_invoice')

def sales_invoice_print(request, invoice_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    invoice = get_object_or_404(Sales_Transaction, pk=invoice_id)
    
    # Get order records
    order_items = invoice.order_records.all()
    
    # Get return records
    return_items = invoice.return_records.all()
    
    # Get payment records
    payments = invoice.payment_records.all()
    
    context = {
        'invoice': invoice,
        'order_items': order_items,
        'return_items': return_items,
        'payments': payments,
        'user_id': user_id,
    }
    return render(request, 'sales_invoice_print.html', context)

def sales_invoice_details(request, invoice_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    invoice = get_object_or_404(Sales_Transaction, pk=invoice_id)
    
    # Get all related records
    order_items = invoice.order_records.all()
    return_items = invoice.return_records.all()
    payments = invoice.payment_records.all()
    
    context = {
        'invoice': invoice,
        'order_items': order_items,
        'return_items': return_items,
        'payments': payments,
        'user_id': user_id,
    }
    return render(request, 'sales_invoice_details.html', context)

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
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if logout_view(request):
        return redirect('home')
    
    active_tab = request.GET.get('tab', 'product')

    # PRODUCT LOGIC
    products_qs = Product.objects.all()
    
    # Get filter inputs
    product_code = request.GET.get('product_code', '').strip().lower()
    description = request.GET.get('description', '').strip().lower()
    status = request.GET.get('status', '').strip()
    
    # Apply filters
    if description:
        products_qs = products_qs.filter(description__icontains=description)
    
    if status:
        products_qs = products_qs.filter(status=status)
    
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
    
    # Generate next product ID (just numbers, 5 digits)
    next_product_id = generate_next_id(Product, 'product_id', 5)
    
    # CUSTOMER LOGIC
    customers_qs = Customer.objects.all()
    
    # Apply customer filters
    customer_name = request.GET.get('customer_name', '').strip()
    contact_person = request.GET.get('contact_person', '').strip()
    phone = request.GET.get('phone', '').strip()
    area = request.GET.get('area', '').strip()
    
    if customer_name:
        customers_qs = customers_qs.filter(name__icontains=customer_name)
    
    if contact_person:
        customers_qs = customers_qs.filter(contact_person__icontains=contact_person)
    
    if phone:
        customers_qs = customers_qs.filter(phone_no__icontains=phone)
    
    if area:
        customers_qs = customers_qs.filter(area=area)
    
    customers = customers_qs.order_by('name')
    
    # Generate next customer ID (4 digits)
    next_customer_id = generate_next_id(Customer, 'customer_id', 4)
    
    # AGENT LOGIC
    agents_qs = Agent.objects.all()
    
    # Apply agent filters
    agent_name = request.GET.get('agent_name', '').strip()
    agent_phone = request.GET.get('agent_phone', '').strip()
    
    if agent_name:
        agents_qs = agents_qs.filter(name__icontains=agent_name)
    
    if agent_phone:
        agents_qs = agents_qs.filter(phone_no__icontains=agent_phone)
    
    agents = agents_qs.order_by('name')
    
    # Generate next agent ID (4 digits)
    next_agent_id = generate_next_id(Agent, 'agent_id', 4)
    
    # BANK LOGIC
    banks_qs = Bank.objects.all()
    
    # Apply bank filters
    bank_acronym = request.GET.get('bank_acronym', '').strip().upper()
    bank_name = request.GET.get('bank_name', '').strip()
    
    if bank_acronym:
        banks_qs = banks_qs.filter(bank_acronym__icontains=bank_acronym)
    
    if bank_name:
        banks_qs = banks_qs.filter(name__icontains=bank_name)
    
    banks = banks_qs.order_by('name')
    
    # Generate next bank ID (4 digits)
    next_bank_id = generate_next_id(Bank, 'bank_id', 4)
    
    # Area choices for customer
    area_choices = Customer.AREA_CHOICES
    
    context = {
        # Products
        'products': products,
        'next_product_id': next_product_id,  # This will be like '00001'
        
        # Customers
        'customers': customers,
        'next_customer_id': next_customer_id,  # This will be like '0001'
        'area_choices': area_choices,
        
        # Agents
        'agents': agents,
        'next_agent_id': next_agent_id,  # This will be like '0001'
        
        # Banks
        'banks': banks,
        'next_bank_id': next_bank_id,  # This will be like '0001'
        
        # Active tab
        'active_tab': active_tab,
        'request': request,
        'user_id': user_id,
    }
    return render(request, 'profiles.html', context)

def product_create(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')  # Will be like '00001'
            product_code = request.POST.get('product_code')  # Alphanumeric code
            description = request.POST.get('description')
            price = float(request.POST.get('price', 0))
            quantity = int(request.POST.get('quantity', 0))
            status = request.POST.get('status', 'Active')
            
            # Check if product code already exists
            if Product.objects.filter(product_code=product_code).exists():
                messages.error(request, f'Product code {product_code} already exists!')
            else:
                product = Product(
                    product_id=product_id,
                    product_code=product_code,
                    description=description,
                    price=price,
                    quantity=quantity,
                    status=status
                )
                product.save()
                messages.success(request, f'Product {description} created successfully!')
                
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
    
    return redirect('profiles')

def product_update(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            product.product_code = request.POST.get('product_code')
            product.description = request.POST.get('description')
            product.price = float(request.POST.get('price', 0))
            product.quantity = int(request.POST.get('quantity', 0))
            product.status = request.POST.get('status', 'Active')
            product.save()
            
            messages.success(request, f'Product {product.description} updated successfully!')
            return redirect('profiles')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    return render(request, 'product_form.html', {'product': product, 'user_id': user_id})

def product_delete(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    product = get_object_or_404(Product, pk=pk)
    description = product.description
    
    try:
        product.delete()
        messages.success(request, f'Product {description} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting product: {str(e)}')
    
    return redirect('profiles')

def customer_create(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_id')
            name = request.POST.get('name')
            contact_person = request.POST.get('contact_person', '')
            phone_no = request.POST.get('phone_no', '')
            address = request.POST.get('address', '')
            area = request.POST.get('area', '')
            
            # Validate phone number format (basic check)
            if phone_no and not (len(phone_no) == 13 and phone_no.startswith('09')):
                messages.error(request, 'Phone number must be in format: 09XX XXX XXXX')
                return redirect('profiles')
            
            customer = Customer(
                customer_id=customer_id,
                name=name,
                contact_person=contact_person,
                phone_no=phone_no,
                address=address,
                area=area
            )
            customer.save()
            messages.success(request, f'Customer {name} created successfully!')
                
        except Exception as e:
            messages.error(request, f'Error creating customer: {str(e)}')
    
    active_tab = request.POST.get('tab', 'customer')
    return redirect(f'/profiles/?tab={active_tab}')

def customer_update(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        try:
            customer.name = request.POST.get('name')
            customer.contact_person = request.POST.get('contact_person', '')
            customer.phone_no = request.POST.get('phone_no', '')
            customer.address = request.POST.get('address', '')
            customer.area = request.POST.get('area', '')
            
            # Validate phone number format (basic check)
            if customer.phone_no and not (len(customer.phone_no) == 13 and customer.phone_no.startswith('09')):
                messages.error(request, 'Phone number must be in format: 09XX XXX XXXX')
                return redirect('profiles')
            
            customer.save()
            
            messages.success(request, f'Customer {customer.name} updated successfully!')
            return redirect('profiles')
            
        except Exception as e:
            messages.error(request, f'Error updating customer: {str(e)}')
    
    return render(request, 'customer_form.html', {'customer': customer, 'user_id': user_id})

def customer_delete(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    customer = get_object_or_404(Customer, pk=pk)
    name = customer.name
    
    try:
        # Check if customer has any sales transactions
        if customer.sales_transactions.exists():
            messages.error(request, f'Cannot delete {name} because they have existing sales transactions.')
        else:
            customer.delete()
            messages.success(request, f'Customer {name} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting customer: {str(e)}')
    
    active_tab = request.GET.get('tab', 'customer')
    return redirect(f'/profiles/?tab={active_tab}')

def agent_create(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            agent_id = request.POST.get('agent_id')
            name = request.POST.get('name')
            phone_no = request.POST.get('phone_no', '')
            
            # Validate phone number format (basic check)
            if phone_no and not (len(phone_no) == 13 and phone_no.startswith('09')):
                messages.error(request, 'Phone number must be in format: 09XX XXX XXXX')
                return redirect('profiles')
            
            # Check if agent with same name exists (optional)
            if Agent.objects.filter(name=name).exists():
                messages.error(request, f'Agent {name} already exists!')
            else:
                agent = Agent(
                    agent_id=agent_id,
                    name=name,
                    phone_no=phone_no
                )
                agent.save()
                messages.success(request, f'Agent {name} created successfully!')
                
        except Exception as e:
            messages.error(request, f'Error creating agent: {str(e)}')
    
    active_tab = request.POST.get('tab', 'agent')
    return redirect(f'/profiles/?tab={active_tab}')

def agent_update(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    agent = get_object_or_404(Agent, pk=pk)
    
    if request.method == 'POST':
        try:
            agent.name = request.POST.get('name')
            agent.phone_no = request.POST.get('phone_no', '')
            
            # Validate phone number format (basic check)
            if agent.phone_no and not (len(agent.phone_no) == 13 and agent.phone_no.startswith('09')):
                messages.error(request, 'Phone number must be in format: 09XX XXX XXXX')
                return redirect('profiles')
            
            agent.save()
            
            messages.success(request, f'Agent {agent.name} updated successfully!')
            return redirect('profiles')
            
        except Exception as e:
            messages.error(request, f'Error updating agent: {str(e)}')
    
    return render(request, 'agent_form.html', {'agent': agent, 'user_id': user_id})

def agent_delete(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    agent = get_object_or_404(Agent, pk=pk)
    name = agent.name
    
    try:
        # Check if agent has any sales transactions
        if agent.sales_transactions.exists():
            messages.error(request, f'Cannot delete {name} because they have existing sales transactions.')
        else:
            agent.delete()
            messages.success(request, f'Agent {name} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting agent: {str(e)}')
    
    active_tab = request.GET.get('tab', 'agent')
    return redirect(f'/profiles/?tab={active_tab}')

def bank_create(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            bank_id = request.POST.get('bank_id')
            bank_acronym = request.POST.get('bank_acronym', '').upper()
            name = request.POST.get('name')
            
            # Check if bank acronym already exists
            if Bank.objects.filter(bank_acronym=bank_acronym).exists():
                messages.error(request, f'Bank acronym {bank_acronym} already exists!')
            else:
                bank = Bank(
                    bank_id=bank_id,
                    bank_acronym=bank_acronym,
                    name=name
                )
                bank.save()
                messages.success(request, f'Bank {name} created successfully!')
                
        except Exception as e:
            messages.error(request, f'Error creating bank: {str(e)}')
    
    active_tab = request.POST.get('tab', 'bank')
    return redirect(f'/profiles/?tab={active_tab}')

def bank_update(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    bank = get_object_or_404(Bank, pk=pk)
    
    if request.method == 'POST':
        try:
            bank.bank_acronym = request.POST.get('bank_acronym', '').upper()
            bank.name = request.POST.get('name')
            bank.save()
            
            messages.success(request, f'Bank {bank.name} updated successfully!')
            return redirect('profiles')
            
        except Exception as e:
            messages.error(request, f'Error updating bank: {str(e)}')
    
    return render(request, 'bank_form.html', {'bank': bank, 'user_id': user_id})

def bank_delete(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')
    
    bank = get_object_or_404(Bank, pk=pk)
    name = bank.name
    
    try:
        # Check if bank is used in any cheque payments
        if bank.cheque_payment_set.exists():
            messages.error(request, f'Cannot delete {name} because it has existing cheque payments.')
        else:
            bank.delete()
            messages.success(request, f'Bank {name} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting bank: {str(e)}')
    
    active_tab = request.GET.get('tab', 'bank')
    return redirect(f'/profiles/?tab={active_tab}')