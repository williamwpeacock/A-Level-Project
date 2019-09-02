from django import forms

class BookForm(forms.Form):
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class' : 'form-field', 'placeholder': 'Add anything you would like the teacher to know here.', 'spellcheck': 'false'}))
