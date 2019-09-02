from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'form-field', 'placeholder': '••••••••'}))

class EnterPINForm(forms.Form):
    pin = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'form-field', 'placeholder': 'XXXX'}))

class RegisterForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'form-field', 'placeholder': '••••••••'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'form-field', 'placeholder': '••••••••'}))
