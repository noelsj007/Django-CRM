from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import Group
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

# Custom imports
from .models import *
from .filters import OrderFilter
from .forms import OrderForm, CreateUserForm, CustomerForm
from .decorators import unauthenticated_user, allowed_users, admin_only


# Create your views here.

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR password is incorrect')
            return render(request, 'accounts/login.html')

    context = {}
    return render(request, 'accounts/login.html', context)


@unauthenticated_user
def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # ------MOVED TO SIGNAL------
            # group = Group.objects.get(name='Customer')
            # user.groups.add(group)
            # Customer.objects.create(
            #     user=user,
            #     name=user.username
            # )

            messages.success(request, 'Account was created for ' + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
# @allowed_users(allowed_roles=['Admin'])
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    # total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    # out_of_delivery = orders.filter(status='Out of Delivery').count()

    context = {'orders': orders, 'customers': customers,
               'total_orders': total_orders, 'pending': pending, 'delivered': delivered}

    return render(request, 'accounts/dashboard.html', context, )


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/product.html', {'products': products})


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)

    orders = customer.order_set.all()
    orders_count = orders.count()

    myfilter = OrderFilter(request.GET, queryset=orders)
    orders = myfilter.qs

    context = {'customer': customer, 'orders': orders, 'orders_count': orders_count, 'myfilter': myfilter}
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def createOrder(request, pk):

    # create_order_form = OrderForm(initial={'customer': customer})
    # queryset=Order.objects.none() -> To prevent display of previous orders

    #  extra=4 -> Number of new enties
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=4)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)

    if request.method == 'POST':
        # create_order_form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'formset': formset}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    update_order_form = OrderForm(instance=order)

    if request.method == 'POST':
        update_order_form = OrderForm(request.POST, instance=order)
        if update_order_form.is_valid():
            update_order_form.save()
            return redirect('/')

    context = {'form': update_order_form}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context = {'item': order}
    return render(request, 'accounts/delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()

    # print(orders)

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders': orders, 'total_orders': total_orders,
               'pending': pending, 'delivered': delivered}

    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def account_setting(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'accounts/account_settings.html', context)
