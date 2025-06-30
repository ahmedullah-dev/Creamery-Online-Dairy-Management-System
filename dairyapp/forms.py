from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from dairyapp.models import Vendor, MilkCategory, Profile, CustomerMilkCategory,Customerledger
import datetime


class contactForm(forms.Form):
    name = forms.CharField(required=True, max_length=100)
    subject = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True)
    message = forms.CharField(required=True,widget=forms.Textarea(attrs={'class': 'form-control','cols':20, 'rows':3 }))


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False,widget=forms.TextInput(attrs={'placeholder': 'Please Enter First Name'}))# help_text='Optional.'
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name','email', 'password1', 'password2')



#*******************************************#
#       ||  Vendors Forms Started  ||       #
#*******************************************#

# Add Vendor
class AddVendorForm(forms.Form):
    CHOICES = (
        ('Cow','Cow'),
        ('Buffaloe','Buffaloe'),
        ('Others','Others'),
    )
    Manager_Name = forms.CharField(required=True, max_length=200,widget=forms.TextInput(attrs={'placeholder': 'Please Manager Name'}))
    Vendor_Name = forms.CharField(required=True, max_length=200,widget=forms.TextInput(attrs={'placeholder': 'Please Enter Name of Vendor'}))
    joining_date = forms.DateField(initial=datetime.date.today)
    Address = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Address of the vendor'}))
    Vendor_Contact = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Mobile Number'}))
    Status =  forms.BooleanField(required=False,initial=True)


# Vendor MilkCategory
class MilkCategoryForm(forms.ModelForm):
    class Meta:
        model = MilkCategory
        fields = ('animalname', 'milkprice','related_vendor')


# Individual vendor dashboard
class vendorledgerForm(forms.Form):
    # def __init__(self,*arg,**kwarg):
    #     print(arg)
    #     print(**kwarg)
    CHOICES1 = (
        ('Cow','Cow'),
        ('Buffaloe','Buffaloe'),
        ('Others','Others'),
    )
    CHOICES2 = (
        ('Sunday','Sunday'),
        ('Monday','Monday'),
        ('Tuesday','Tuesday'),
        ('Wednesday','Wednesday'),
        ('Thursday','Thursday'),
        ('Friday','Friday'),
        ('Saturday','Saturday'),
    )
    Milk_Category = forms.ChoiceField(label='',choices=CHOICES1)
    #Vendor_Name = forms.CharField(label='',required=True, max_length=200)
    #Manager_Name = forms.CharField(label='',required=True, max_length=200)
    Day = forms.ChoiceField(label='',choices=CHOICES2)
    Quantity = forms.CharField(label='',required=False)



#***************************************************#
#       ||  Customer Forms (User) Started  ||       #
#***************************************************#

# Add Customer - This is a Profile model (For Create Admin/Manager/Customer)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('user','user_type','contact_number','joining_data','address')


# Customer MilkCategory
class CustomerMilkCategoryForm(forms.ModelForm):
    class Meta:
        model = CustomerMilkCategory
        fields = ('animalname','milkprice','related_customer')


from django import forms
from .models import UserRegistrationModel


class UserRegistrationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[a-zA-Z]+'}), required=True, max_length=100)
    loginid = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[a-zA-Z]+'}), required=True, max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'pattern': '(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}',
                                                                 'title': 'Must contain at least one number and one uppercase and lowercase letter, and at least 8 or more characters'}),
                               required=True, max_length=100)
    mobile = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[56789][0-9]{9}'}), required=True,
                             max_length=100)
    email = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'}),
                            required=True, max_length=100)
    locality = forms.CharField(widget=forms.TextInput(), required=True, max_length=100)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 22}), required=True, max_length=250)
    city = forms.CharField(widget=forms.TextInput(
        attrs={'autocomplete': 'off', 'pattern': '[A-Za-z ]+', 'title': 'Enter Characters Only '}), required=True,
        max_length=100)
    state = forms.CharField(widget=forms.TextInput(
        attrs={'autocomplete': 'off', 'pattern': '[A-Za-z ]+', 'title': 'Enter Characters Only '}), required=True,
        max_length=100)
    status = forms.CharField(widget=forms.HiddenInput(), initial='waiting', max_length=100)

    class Meta():
        model = UserRegistrationModel
        fields = '__all__'


