from django import forms

from pebookingsystem.models import *

class StudentForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    pin = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class' : 'form-checkbox'}))
    fullname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    schoolyear = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'form-field'}))
    parents = forms.ModelMultipleChoiceField(required=False, queryset=Parent.objects.all(), widget=forms.SelectMultiple(attrs={'class' : 'form-field'}))
    schoolclasses = forms.ModelMultipleChoiceField(required=False, queryset=SchoolClass.objects.all(), widget=forms.SelectMultiple(attrs={'class' : 'form-field'}))

class ParentForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    pin = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class' : 'form-checkbox'}))
    fullname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    children = forms.ModelMultipleChoiceField(required=False, queryset=Student.objects.all(), widget=forms.SelectMultiple(attrs={'class' : 'form-field'}))

class TeacherForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    pin = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class' : 'form-checkbox'}))
    fullname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    title = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    schoolclasses = forms.ModelMultipleChoiceField(required=False, queryset=SchoolClass.objects.all(), widget=forms.SelectMultiple(attrs={'class' : 'form-field'}))

class AdminForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    pin = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class' : 'form-checkbox'}))
    fullname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))

class ClassForm(forms.Form):
    classname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    schoolyear = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'form-field'}))
    students = forms.ModelMultipleChoiceField(required=False, queryset=Student.objects.all(), widget=forms.SelectMultiple(attrs={'class' : 'form-field'}))
    teachers = forms.ModelMultipleChoiceField(required=False, queryset=Teacher.objects.all(), widget=forms.SelectMultiple(attrs={'class' : 'form-field'}))
    pes = forms.ModelMultipleChoiceField(required=False, queryset=ParentsEvening.objects.all(), widget=forms.SelectMultiple(attrs={'class' : 'form-field'}))
    details = forms.CharField(required=False, widget=forms.Textarea(attrs={'class' : 'form-textarea', 'spellcheck': 'false'}))

class ParentsEveningForm(forms.Form):
    pename = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-field'}))
    date = forms.DateField(input_formats=['%d/%m/%y', '%d/%m/%Y'], widget=forms.DateInput(attrs={'class' : 'form-field', 'placeholder': 'dd/mm/yyyy'}))
    starttime = forms.TimeField(input_formats=['%H:%M'], widget=forms.TimeInput(attrs={'class' : 'form-field', 'placeholder': 'hh:mm'}))
    endtime = forms.TimeField(input_formats=['%H:%M'], widget=forms.TimeInput(attrs={'class' : 'form-field', 'placeholder': 'hh:mm'}))
    appointmentlength = forms.TimeField(input_formats=['%H:%M'], widget=forms.TimeInput(attrs={'class' : 'form-field', 'placeholder': 'hh:mm'}))
    schoolclasses = forms.ModelMultipleChoiceField(required=False, queryset=SchoolClass.objects.all(), widget=forms.SelectMultiple(attrs={'class' : 'form-field'}))
    details = forms.CharField(required=False, widget=forms.Textarea(attrs={'class' : 'form-textarea', 'spellcheck': 'false'}))
