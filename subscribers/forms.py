from django import forms

class SubscriptionForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class PasswordCreationForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
