from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from dairyapp import models
from django.shortcuts import get_object_or_404
from dairyapp.forms import contactForm, SignUpForm, AddVendorForm, MilkCategoryForm, vendorledgerForm, ProfileForm, \
    CustomerMilkCategoryForm
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required


from .forms import UserRegistrationForm
from .models import UserRegistrationModel

from .models import Vendor, Profile


def home(request):
    temp = 'home.html'
    return render(request, temp, {})


def loginForm(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("Login ID = ", username, ' Password = ', password)
        try:
            check = UserRegistrationModel.objects.get(loginid=username, password=password)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                vid = models.Vendor.objects.get(vendorname=username)
                request.session['vid'] = vid.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = username
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'login.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'login.html', {})


def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})


def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'signup.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})


def AdminsCheck(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'admin' and password == 'admin':
            return render(request, 'admins/AdminHome.html')
        else:
            messages.success(request, 'Please Check Your Login Details')
            return render(request, 'AdminLogin.html', {})
    else:
        return render(request, 'AdminLogin.html', {})


def AdminsHome(request):
    return render(request, 'admins/AdminHome.html')


def RegisterUsersView(request):
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/viewregisterusers.html', {'data': data})


def ActivateUsers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        data = UserRegistrationModel.objects.all()
        return render(request, 'admins/viewregisterusers.html', {'data': data})


# *******************************************#
#       ||  Vendors Views Started  ||       #
# *******************************************#

# Add Vendor
# @login_required
def addvendor(request):
    vl = UserRegistrationModel.objects.only('loginid')
    if request.method == 'POST':
        form = AddVendorForm(request.POST)
        if form.is_valid():
            managername = form.cleaned_data['Manager_Name']
            vendorname = form.cleaned_data['Vendor_Name']
            address = form.cleaned_data['Address']
            vendorcontact = form.cleaned_data['Vendor_Contact']
            status = form.cleaned_data['Status']
            v = models.Vendor(managername=managername, vendorname=vendorname, address=address,
                              vendorcontact=vendorcontact, status=status)
            v.save()
            return redirect('add_milk_category')  # milkcategoryform.html
    else:
        form = AddVendorForm()

        return render(request, 'admins/addvendor.html', {'form': form, 'vl': vl})


# Vendor MilkCategory
# @login_required
def add_milk_category(request):
    vl = UserRegistrationModel.objects.only('loginid')
    if request.method == 'POST':
        form = MilkCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            # return redirect('add_milk_category')
            return render(request, 'admins/AdminHome.html')
    else:
        form = MilkCategoryForm()
        return render(request, 'admins/milkcategoryform.html', {'form': form, 'vl': vl})


# All vendors dashboard
# @login_required
def allvendor(request):
    manager = ''
    # print(manager)
    # Vendor.objects.all().delete()
    vendor = models.Vendor.objects.all()
    return render(request, 'admins/allvendor.html', {'vendor': vendor})


# Individual vendor dashboard
# @login_required
def ledger(request, pk):
    ledgerform = vendorledgerForm()
    # data = vendorledger.objects.filter(managername=request.user.username)
    vendor_obj = get_object_or_404(models.Vendor, pk=pk)
    # pkvalue = vendor_obj.pk
    # print(pkvalue)
    # url1 = request.path
    # print(url1)
    ledgerdata = models.vendorledger.objects.filter(related_vendor=vendor_obj)
    alltotal = 0.0
    # print(ledgerdata[0].total)
    for alto in ledgerdata:
        alltotal = alltotal + float(alto.total)
    print(alltotal)
    # print(vendor_obj)
    # print(ledgerdata)
    milks = models.MilkCategory.objects.filter(related_vendor=vendor_obj)
    # for milk in milks:
    #    print(milk.animalname + "-----" +milk.milkprice)
    milk_list = [(milk.animalname + "-" + str(milk.milkprice), milk.pk) for milk in milks]
    print(milk_list)
    # print(tuple(milk_list))
    day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return render(request, 'admins/vendorledger.html', {
        "vendor_obj": vendor_obj,
        "ledgerdata": ledgerdata,
        "ledgerform": ledgerform,
        "num_range": range(6),
        "milk_list": milk_list,
        "day_list": day_list,
        "alltotal": alltotal,
    })


def ledger_save(request):
    if request.method == 'POST':
        print(request.POST.dict())
        print(request.POST.get("milktype", ""))
        vendor_pk = request.POST.get("vendor", None)
        date = request.POST.get("date", None)
        milkcategory_pk = request.POST.get("milktype", None)
        quantity = request.POST.get("quantity", None)
        related_vendor = models.Vendor.objects.get(pk=vendor_pk)
        related_milkcategory = models.MilkCategory.objects.get(pk=milkcategory_pk)
        price = related_milkcategory.milkprice
        total = float(quantity) * float(price)
        path = request.path
        pathstr = str(path)

        # alltotal = models.vendorledger.objects.filter(pk=pk)
        # print(related_vendor,date, related_milkcategory, price, quantity, total)

        g = models.vendorledger(
            related_vendor=related_vendor,
            date=date,
            related_milkcategory=related_milkcategory,
            price=price,
            quantity=quantity,
            total=total
        )
        g.save()
        current_url = "/ledger/" + str(vendor_pk) + "/"
        return redirect(current_url)


def ledger_delete(request):
    if request.method == 'POST':
        # print(request.POST.get('ledger_pk'))
        pk = request.POST.get('ledger_pk')
        ledger_entry = models.vendorledger.objects.get(pk=pk)
        vendor_pk = ledger_entry.related_vendor.pk
        ledger_entry.delete()
        current_url = "/ledger/" + str(vendor_pk) + "/"
    return redirect(current_url)


# ***************************************************#
#       ||  Customer Views (User) Started  ||       #
# ***************************************************#

# Add Customer - This is a Profile model (For Create Admin/Manager/Customer)
# @login_required
def addcustomer(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        # print("i am in addcustomer upper")
        if form.is_valid():
            # print("i am in addcustomer")
            form.save()
            return redirect('customer_milk_category')
    else:
        form = ProfileForm()
    return render(request, 'Customers/Add_Customer.html', {'form': form})


# Customer MilkCategory
def customer_milk_category(request):
    cl = Profile.objects.only('user')
    if request.method == 'POST':
        form = CustomerMilkCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomerMilkCategoryForm()
    return render(request, 'Customers/customer_milk_category.html', {'form': form, 'cl': cl})


# Customer_page
def Customer_page(request):
    print("Username=", request.user)
    print("Userpk=", request.user.pk)
    customer = request.user
    customer_info = models.Customerledger.objects.filter(related_customer=customer)
    alltotal = 0.0
    for i in customer_info:
        alltotal = alltotal + float(i.total)
    print(alltotal)
    for data in customer_info:
        print("Customer Name: ", data.related_customer)
        print("joining Date: ", data.date)
        print("Quantity: ", data.price)
        print("Total: ", data.total)

    return render(request, 'Customers/customer.html', {'customer_info': customer_info, 'alltotal': alltotal})


# Customer ledger
def customer_ledger(request, pk):
    ledgerform = vendorledgerForm()
    # data = vendorledger.objects.filter(managername=request.user.username)
    vendor_obj = get_object_or_404(models.Vendor, pk=pk)
    # pkvalue = vendor_obj.pk
    # print(pkvalue)
    # url1 = request.path
    # print(url1)
    ledgerdata = models.vendorledger.objects.filter(related_vendor=vendor_obj)
    alltotal = 0.0
    # print(ledgerdata[0].total)
    for alto in ledgerdata:
        alltotal = alltotal + float(alto.total)
    print(alltotal)
    # print(vendor_obj)
    # print(ledgerdata)
    milks = models.MilkCategory.objects.filter(related_vendor=vendor_obj)
    # for milk in milks:
    #    print(milk.animalname + "-----" +milk.milkprice)
    milk_list = [(milk.animalname + "-" + str(milk.milkprice), milk.pk) for milk in milks]
    print(milk_list)
    # print(tuple(milk_list))
    day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return render(request, 'users/users_ledger.html', {
        # "customer_full_name": customer_full_name,
        # "milk_list": milk_list,
        # "customer_obj": customer_obj,
        # "customer_ledger_info": customer_ledger_info,
        # "alltotal": alltotal,
        "vendor_obj": vendor_obj,
        "ledgerdata": ledgerdata,
        "ledgerform": ledgerform,
        "num_range": range(6),
        "milk_list": milk_list,
        "day_list": day_list,
        "alltotal": alltotal,
    })


def customer_ledger_save(request):
    if request.method == 'POST':
        print(request.POST.dict())
        customer_pk = request.POST.get("customer", None)
        date = request.POST.get("date", None)
        milk_pk = request.POST.get("milktype", None)
        quantity = request.POST.get("quantity", None)
        related_customer = models.User.objects.get(pk=customer_pk)
        related_milk_category = models.CustomerMilkCategory.objects.get(pk=milk_pk)
        price = related_milk_category.milkprice
        total = float(quantity) * float(price)

        data = models.Customerledger(
            related_customer=related_customer,
            date=date,
            related_milk_category=related_milk_category,
            quantity=quantity,
            price=price,
            total=total,
        )
        data.save()
        current_url = "/customer_ledger/" + str(customer_pk) + "/"
        return redirect(current_url)


def customer_ledger_delete(request):
    if request.method == 'POST':
        pk = request.POST.get('customer_pk')
        customer_ledger_entry = models.Customerledger.objects.get(pk=pk)
        customer_ledger_entry.delete()
        customer_pk = customer_ledger_entry.related_customer.pk
        current_url = "/customer_ledger/" + str(customer_pk) + "/"
        return redirect(current_url)


@login_required
def allcustomer(request):
    customerinfo = models.Profile.objects.all()
    return render(request, 'Customers/Customer_detail.html', {'customerinfo': customerinfo})

# def password_reset(request):
#     if request.method == 'POST':
#         form = password_reset_form(request.POST)
#         if form.is_valid():
#             subject = "Password Reset"
#             to_email = form.cleaned_data['email']
#             receivers_list = [to_email,]
#             message =
#
#             emailsender = settings.EMAIL_HOST_USER
#             send_mail(subject, message, emailsender, receivers_list, fail_silently=False)
#             print("To Email: ",to_email)
#             return redirect('home')
#     else:
#         form = password_reset_form()
#         return render(request,'registration/password_reset_form.html',{'form':form})
from django.core.management import call_command
from django.http import HttpResponse
import os

def migrate_now(request):
    if os.environ.get('RENDER'):
        try:
            call_command('makemigrations')
            call_command('migrate')
            return HttpResponse("✅ Migration successful on Render!")
        except Exception as e:
            return HttpResponse(f"❌ Migration failed: {str(e)}")
    return HttpResponse("Not on Render.")
