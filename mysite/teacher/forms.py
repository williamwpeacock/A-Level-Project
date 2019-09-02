from django import forms

class BookForm(forms.Form):
    student = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'id' : 'student-selection'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class' : 'form-field', 'placeholder': 'Add anything you would like the teacher to know here.', 'spellcheck': 'false'}))

    def __init__(self, *args, **kwargs):
        students = kwargs.pop('students', None)
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = students
