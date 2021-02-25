from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE

PAYMENT_CHOICES = (
    ('InstaMojo', 'Online(Debit/Credit Cards'),
    #('RazorPay', 'Online(Debit/Credit Cards, All Wallets, BHIM UPI)'),
    ('COD', 'Cash On Delivery')
)



class CreateUserForm(UserCreationForm):
	contact_number = forms.CharField(max_length=255)
	alt_contact_number = forms.CharField(max_length=255)

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2', 'first_name', 'contact_number', 'alt_contact_number')

	def clean_contact_number(self):
		contact_number = self.cleaned_data['contact_number']
		print(contact_number)
		if len(contact_number) != 8 or int(contact_number[0]) < 6:
			raise ValidationError('Please enter a correct number!')
		return contact_number

	
        
class UserLogInForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        fields = '__all__'

    def clean_username(self):
    	username = self.cleaned_data['username']
    	try:
    		exists = User.objects.get(username=username).groups.filter(name='customers').exists()
    		if exists:
    			pass
    		else:
    			raise ValidationError('This user is not authenticated as Service Provider!')
    	except Exception as e:
    		print(str(e))
    		raise ValidationError('This user is not authenticated as Service Provider!')
    	return username


class ServiceLogInForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        fields = '__all__'

    def clean_username(self):
    	username = self.cleaned_data['username']
    	print('______________________________________')
    	try:
    		exists = User.objects.get(username=username).groups.filter(name='service_providers').exists()
    		if exists:
    			pass
    		else:
    			raise ValidationError('This user is not authenticated as Service Provider!')
    	except Exception as e:
    		print(str(e))
    		raise ValidationError('This user is not authenticated as Service Provider!')
    	return username


class CreateProductForm(forms.Form):
    Product_Description = forms.CharField(widget=TinyMCE(attrs={ 'class':"col-lg-8 col-sm-12 form"}))
    Shipping_Details = forms.CharField(widget=TinyMCE(attrs={ 'class':"col-lg-8 col-sm-12 form"}))
    class Meta:
        fields = '__all__'


class FileUploadForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        fields = '__all__'

class RadioCheckoutForm(forms.Form):
    payment_option =  forms.CharField(widget=forms.RadioSelect(choices=PAYMENT_CHOICES, attrs={'class':"my-radio"}))
