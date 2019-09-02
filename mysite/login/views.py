from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate, logout

from . import forms
from pebookingsystem.models import User, Admin, Teacher, Parent, Student
from pebookingsystem import functions

class LoginView(TemplateView):
    template_name = 'login/login.html'

    def get(self, request):

        # Creates form and passes it to template to render
        form = forms.LoginForm()
        args = {'form': form}
        return render(request, self.template_name, args)

    def post(self, request):

        # Creates form and passes it to process_form()
        form = forms.LoginForm(request.POST)
        return self.process_form(request, form)

    def process_form(self, request, form):

        # Create dictionary incase form needs to be re-rendered
        # Checks if form is valid
        args = {'form': form}
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the 'username' and 'password' fields
            cleaned_data = form.cleaned_data
            username = cleaned_data['username']
            password = cleaned_data['password']

            # Tries to authenticate with the given username and password
            # If authenticate() returns user, logs in and redirects to welcome
            user = authenticate(username=username, password=password)
            if user != None:
                login(request, user)
                return self.role_redirect(request, user, args)
            else:
                
                # If there are no accounts on the system, an Admin account is created with a random PIN
                if len(User.objects.all()) == 0:
                    newuser = User(username="admin", role="Admin", pin=functions.generate_pin())
                    newuser.save()

                    newperson = Admin(user=newuser, fullname="Default Admin")
                    newperson.save()

                    login(request, newuser)
                    return self.role_redirect(request, newuser, args)
                else:
                    args['error_message'] = '× Incorrect username or password.'
        else:
            args['error_message'] = '× Incorrect username or password.'

        return render(request, self.template_name, args)

    # Redirects to correct Welcome page or displays error message if user does not have valid role
    def role_redirect(self, request, user, args):
        if user.role == "Admin":
            return redirect('admin:welcome')
        elif user.role == "Teacher":
            return redirect('teacher:welcome')
        elif user.role == "Parent":
            return redirect('parent:welcome')
        elif user.role == "Student":
            return redirect('student:welcome')
        else:
            args['error_message'] = '× Something went wrong.'
            return render(request, self.template_name, args)

class EnterPINView(TemplateView):
    template_name = 'login/enterpin.html'

    def get(self, request):

        # Creates form and passes it to template to render
        form = forms.EnterPINForm()
        args = {'form': form}
        return render(request, self.template_name, args)

    def post(self, request):

        # Creates form and passes it to process_form()
        form = forms.EnterPINForm(request.POST)
        return self.process_form(request, form)

    def process_form(self, request,form):

        # Create dictionary incase form needs to be re-rendered
        # Checks if form is valid
        args = {'form': form}
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the 'pin' field
            cleaned_data = form.cleaned_data
            pin = cleaned_data['pin']

            # If given PIN corresponds to account, redirect to register with that PIN
            users = User.objects.filter(pin=pin)
            if len(users) == 1:
                return redirect('login:register', pin)
            else:
                args['error_message'] = '× The PIN you entered was not valid.'
                return render(request, self.template_name, args)
        else:
            args['error_message'] = '× The PIN you entered was not valid.'
            return render(request, self.template_name, args)

class RegisterView(TemplateView):
    template_name = 'login/register.html'

    def get(self, request, pin):

        # Checks if PIN corresponds to user
        # Gets user
        users = User.objects.filter(pin=pin)
        if len(users) == 1:
            user = users[0]

            # Checks if user corresponds to person
            # Gets person using get_person()
            person = functions.get_person(user)
            if person != None:

                # Creates form and 'args' dictionary
                # Passes them to template to render
                form = forms.RegisterForm()
                args = {'fullname': person.fullname, 'form': form}
                return render(request, self.template_name, args)
            else:
                return redirect('login:login')
        else:
            return redirect('login:enterpin')

    def post(self, request, pin):

        # Checks if PIN corresponds to user
        # Gets user
        users = User.objects.filter(pin=pin)
        if len(users) == 1:
            user = users[0]

            # Checks if user corresponds to person
            # Gets person using get_person()
            person = functions.get_person(user)
            if person != None:

                # Creates form and 'args' dictionary
                form = forms.RegisterForm(request.POST)
                args = {'fullname': person.fullname, 'form': form}
                return self.process_form(request, user, form, args)
            else:
                return redirect('login:login')
        else:
            return redirect('login:enterpin')

    def process_form(self, request, user, form, args):

        # Checks if form is valid
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the 'password1' and 'password2' fields
            cleaned_data = form.cleaned_data
            password1 = cleaned_data['password1']
            password2 = cleaned_data['password2']

            # Checks if given passwords are equal, contain spaces, and they are within a certain range
            if password1 == password2:
                if " " not in password1:
                    if 8 <= len(password1) <= 30:

                        # Sets password to the one given
                        # Sets PIN to NULL
                        user.set_password(password1)
                        user.pin = None
                        user.save()

                        # Login and redirect to Success
                        login(request, user)
                        return redirect('login:success')
                    else:
                        args['error_message'] = '× Passwords must be 8-30 characters long.'
                        return render(request, self.template_name, args)
                else:
                    args['error_message'] = '× Passwords must not contain spaces.'
                    return render(request, self.template_name, args)
            else:
                args['error_message'] = '× Passwords do not match.'
                return render(request, self.template_name, args)
        else:
            args['error_message'] = '× Invalid password.'
            return render(request, self.template_name, args)

class SuccessView(TemplateView):
    template_name = 'login/success.html'

    def get(self, request):
        user = request.user

        # Checks user is logged in
        # Gets person corresponding to this user
        if user.is_authenticated:
            person = functions.get_person(user)

            # Checks person exists
            # Creates dictionary and passes it to template to be rendered
            if person != None:
                args = {'username': user.username, 'role': user.role, 'fullname': person.fullname}
                return render(request, self.template_name, args)
            else:
                return redirect('login:logout')
        else:
            return redirect('login:login')

# Gets user and checks if they are logged in
# If so, logs them out
# Redirects to Login
def my_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
    return redirect('login:login')
