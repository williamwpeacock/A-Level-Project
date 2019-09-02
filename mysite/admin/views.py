from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView

from pebookingsystem.models import *
from pebookingsystem import functions
from . import forms

class WelcomeView(TemplateView):
    template_name = 'admin/welcome.html'

    def get(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Creates the dictionary to be passed to the template
                    # Gets number of each role and number of classes and parents' evenings
                    args = {'username': user.username, 'fullname': admin.fullname}
                    args['students'] = Student.objects.all().count()
                    args['parents'] = Parent.objects.all().count()
                    args['teachers'] = Teacher.objects.all().count()
                    args['admins'] = Admin.objects.all().count()
                    args['pes'] = ParentsEvening.objects.all().count()
                    args['schoolclasses'] = SchoolClass.objects.all().count()

                    # Renders template
                    return render(request, self.template_name, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class AccountsView(TemplateView):
    template_name = 'admin/accounts.html'

    def get(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Creates the dictionary to be passed to the template
                    # Gets the table of users using get_users()
                    args = {'username': user.username}
                    args['users'] = self.get_users()

                    # Renders template
                    return render(request, self.template_name, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def get_users(self):

        # Gets all users
        all_users = User.objects.all()
        users_table = []

        # Loops through all users then gets their corresponding Student, Parent, Teacher, or Admin record
        for user in all_users:
            if user.role == "Student":
                person = Student.objects.filter(user=user)
            elif user.role == "Parent":
                person = Parent.objects.filter(user=user)
            elif user.role == "Teacher":
                person = Teacher.objects.filter(user=user)
            elif user.role == "Admin":
                person = Admin.objects.filter(user=user)
            else:
                person = []

            # Appends the row to the final list in the form [id, username, full name, role, pin]
            if len(person) == 1:
                users_table.append([user.id, user.username, person[0].fullname, user.role, user.pin])

        return users_table

class AddAccountView(TemplateView):
    template_name = 'admin/account.html'

    def get(self, request, role):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Creates the dictionary to be passed to the template
                    # Gets the correct form and adds it to the dictionary
                    args = {'username': user.username, 'mode': 'Add'}
                    if role == "student":
                        args['role'] = "Student"
                        form = forms.StudentForm()
                    elif role == "parent":
                        args['role'] = "Parent"
                        form = forms.ParentForm()
                    elif role == "teacher":
                        args['role'] = "Teacher"
                        form = forms.TeacherForm()
                    elif role == "admin":
                        args['role'] = "Admin"
                        form = forms.AdminForm()

                    args['form'] = form

                    # Renders template
                    return render(request, self.template_name, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def post(self, request, role):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Creates the dictionary to be passed to the template
                    # Gets the correct form and adds it to the dictionary
                    args = {'username': user.username, 'mode': 'Add'}
                    if role == "student":
                        args['role'] = "Student"
                        form = forms.StudentForm(request.POST)
                    elif role == "parent":
                        args['role'] = "Parent"
                        form = forms.ParentForm(request.POST)
                    elif role == "teacher":
                        args['role'] = "Teacher"
                        form = forms.TeacherForm(request.POST)
                    elif role == "admin":
                        args['role'] = "Admin"
                        form = forms.AdminForm(request.POST)

                    args['form'] = form

                    return self.process_form(request, role, form, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def process_form(self, request, role, form, args):

        # Checks if form is valid
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the 'username' and 'pin' fields
            cleaned_data = form.cleaned_data
            username = cleaned_data['username']
            pin_bool = cleaned_data['pin']

            # Gets all users with a conflicting username
            # Checks username is free
            conflicts = User.objects.filter(username=username)
            if len(conflicts) == 0:

                # If 'User PIN?' is checked, generate free PIN using generate_pin()
                # If not, set pin = None
                if pin_bool:
                    pin = functions.generate_pin()
                    if pin == 0:
                        args['error_message'] = '× All PINs have been taken.'
                        return render(request, self.template_name, args)
                else:
                    pin = None

                # Calls correct add function based on the role passed in the URL
                if role == "student":
                    self.add_student(cleaned_data, username, pin)
                elif role == "parent":
                    self.add_parent(cleaned_data, username, pin)
                elif role == "teacher":
                    self.add_teacher(cleaned_data, username, pin)
                elif role == "admin":
                    self.add_admin(cleaned_data, username, pin)

                # Redirects back to Accounts page
                return redirect('admin:accounts')
            else:
                args['error_message'] = '× User with that username already exists.'
                return render(request, self.template_name, args)
        else:
            args['error_message'] = '× Something went wrong, please try again.'
            return render(request, self.template_name, args)



    def add_student(self, cleaned_data, username, pin):

        # Gets contents of remaining fields
        fullname = cleaned_data['fullname']
        schoolyear = cleaned_data['schoolyear']
        parents = cleaned_data['parents']
        schoolclasses = cleaned_data['schoolclasses']

        # Creates User and Student records
        newuser = User(username=username, role="Student", pin=pin)
        newuser.save()

        newperson = Student(user=newuser, fullname=fullname, schoolyear=schoolyear)
        newperson.save()

        # Creates relationships between other tables
        for parent in parents:
            parent.children.add(newperson)

        for schoolclass in schoolclasses:
            schoolclass.students.add(newperson)

    def add_parent(self, cleaned_data, username, pin):

        # Gets contents of remaining fields
        fullname = cleaned_data['fullname']
        children = cleaned_data['children']

        # Creates User and Parent records
        newuser = User(username=username, role="Parent", pin=pin)
        newuser.save()

        newperson = Parent(user=newuser, fullname=fullname)
        newperson.save()

        # Creates relationships between other tables
        for child in children:
            newperson.children.add(child)

    def add_teacher(self, cleaned_data, username, pin):

        # Gets contents of remaining fields
        fullname = cleaned_data['fullname']
        title = cleaned_data['title']
        subject = cleaned_data['subject']
        schoolclasses = cleaned_data['schoolclasses']

        # Creates User and Teacher records
        newuser = User(username=username, role="Teacher", pin=pin)
        newuser.save()

        newperson = Teacher(user=newuser, fullname=fullname, title=title, subject=subject)
        newperson.save()

        # Creates relationships between other tables
        for schoolclass in schoolclasses:
            schoolclass.teachers.add(newperson)

    def add_admin(self, cleaned_data, username, pin):

        # Gets contents of remaining fields
        fullname = cleaned_data['fullname']

        # Creates User and Admin records
        newuser = User(username=username, role="Admin", pin=pin)
        newuser.save()

        newperson = Admin(user=newuser, fullname=fullname)
        newperson.save()

class EditAccountView(TemplateView):
    template_name = 'admin/account.html'

    def get(self, request, account_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Checks if id passed in the URL corresponds to account
                    # Gets the account
                    accounts = User.objects.filter(id=account_id)
                    if len(accounts) == 1:
                        account = accounts[0]

                        # Gets the starting value of the 'Use PIN?' checkbox
                        if account.pin != None:
                            pin_bool = True
                        else:
                            pin_bool = False

                        # Creates the dictionary to be passed to the template
                        args = {'username': user.username, 'mode': 'Edit', 'account_id': account_id, 'role': account.role}

                        # Creates and populates form based on role of account
                        if account.role == "Student":

                            # Checks if the person exists
                            # Gets the person
                            people = Student.objects.filter(user=account)
                            if len(people) == 1:
                                person = people[0]

                                # Populates the form with the person's details
                                form = forms.StudentForm(initial={'username': account.username,
                                                                  'pin': pin_bool,
                                                                  'fullname': person.fullname,
                                                                  'schoolyear': person.schoolyear,
                                                                  'parents': Parent.objects.filter(children=person),
                                                                  'schoolclasses': SchoolClass.objects.filter(students=person)})
                            else:
                                return redirect('admin:accounts')
                        elif account.role == "Parent":

                            # Checks if the person exists
                            # Gets the person
                            people = Parent.objects.filter(user=account)
                            if len(people) == 1:
                                person = people[0]

                                # Populates the form with the person's details
                                form = forms.ParentForm(initial={'username': account.username,
                                                                 'pin': pin_bool,
                                                                 'fullname': person.fullname,
                                                                 'children': Student.objects.filter(parent=person)})
                            else:
                                return redirect('admin:accounts')
                        elif account.role == "Teacher":

                            # Checks if the person exists
                            # Gets the person
                            people = Teacher.objects.filter(user=account)
                            if len(people) == 1:
                                person = people[0]

                                # Populates the form with the person's details
                                form = forms.TeacherForm(initial={'username': account.username,
                                                                  'pin': pin_bool,
                                                                  'fullname': person.fullname,
                                                                  'title': person.title,
                                                                  'subject': person.subject,
                                                                  'schoolclasses': SchoolClass.objects.filter(teachers=person)})
                            else:
                                return redirect('admin:accounts')
                        elif account.role == "Admin":

                            # Checks if the person exists
                            # Gets the person
                            people = Admin.objects.filter(user=account)
                            if len(people) == 1:
                                person = people[0]

                                # Populates the form with the person's details
                                form = forms.AdminForm(initial={'username': account.username,
                                                                'pin': pin_bool,
                                                                'fullname': person.fullname})
                            else:
                                return redirect('admin:accounts')
                        else:
                            return redirect('admin:accounts')


                        args['form'] = form

                        # Renders template
                        return render(request, self.template_name, args)
                    else:
                        return redirect('admin:accounts')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def post(self, request, account_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins.filter(user=user)
                    if len(admins) == 1:
                        admin = admins[0]

                        # Checks if id passed in the URL corresponds to account
                        # Gets the account
                        accounts = User.objects.filter(id=account_id)
                        if len(accounts) == 1:
                            account = accounts[0]

                            # Creates the dictionary to be passed to the template
                            args = {'username': user.username, 'mode': 'Edit', 'account_id': account_id, 'role': account.role}

                            # Creates form based on role of account
                            if account.role == "Student":

                                # Checks if the person exists
                                # Gets the person
                                people = Student.objects.filter(user=account)
                                if len(people) == 1:
                                    person = people[0]

                                    form = forms.StudentForm(request.POST)
                                else:
                                    return redirect('admin:accounts')
                            elif account.role == "Parent":

                                # Checks if the person exists
                                # Gets the person
                                people = Parent.objects.filter(user=account)
                                if len(people) == 1:
                                    person = people[0]

                                    form = forms.ParentForm(request.POST)
                                else:
                                    return redirect('admin:accounts')
                            elif account.role == "Teacher":

                                # Checks if the person exists
                                # Gets the person
                                people = Teacher.objects.filter(user=account)
                                if len(people) == 1:
                                    person = people[0]

                                    form = forms.TeacherForm(request.POST)
                                else:
                                    return redirect('admin:accounts')
                            elif account.role == "Admin":

                                # Checks if the person exists
                                # Gets the person
                                people = Admin.objects.filter(user=account)
                                if len(people) == 1:
                                    person = people[0]

                                    form = forms.AdminForm(request.POST)
                                else:
                                    return redirect('admin:accounts')
                            else:
                                return redirect('admin:accounts')

                            args['form'] = form

                            return self.process_form(request, account, person, form, args)
                        else:
                            return redirect('admin:accounts')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def process_form(self, request, account, person, form, args):

        # Checks if form is valid
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the 'username' and 'pin' fields
            cleaned_data = form.cleaned_data
            username = cleaned_data['username']
            pin_bool = cleaned_data['pin']


            # Gets all users with a conflicting username
            # Checks username is free or username hasn't changed
            conflicts = User.objects.filter(username=username)
            if len(conflicts) == 0 or username == account.username:

                # If 'User PIN?' is checked and account doesn't have one, generate free PIN using generate_pin()
                # If 'User PIN?' is checked and account does have one, use the same one
                # If not checked, set pin = None
                if pin_bool and account.pin == None:
                    pin = functions.generate_pin()
                    if pin == 0:
                        args['error_message'] = '× All PINs have been taken.'
                        return render(request, self.template_name, args)
                elif pin_bool and account.pin != None:
                    pin = account.pin
                else:
                    pin = None

                # Calls correct edit function based on the role passed in the URL
                if account.role == "Student":
                    self.edit_student(account, person, cleaned_data, username, pin)
                elif account.role == "Parent":
                    self.edit_parent(account, person, cleaned_data, username, pin)
                elif account.role == "Teacher":
                    self.edit_teacher(account, person, cleaned_data, username, pin)
                elif account.role == "Admin":
                    self.edit_admin(account, person, cleaned_data, username, pin)

                # Redirects back to Accounts page
                return redirect('admin:accounts')
            else:
                args['error_message'] = '× User with that username already exists.'
                return render(request, self.template_name, args)
        else:
            args['error_message'] = '× Something went wrong, please try again.'
            return render(request, self.template_name, args)

    def edit_student(self, account, person, cleaned_data, username, pin):

        # Gets contents of remaining fields
        fullname = cleaned_data['fullname']
        schoolyear = cleaned_data['schoolyear']
        parents = cleaned_data['parents']
        schoolclasses = cleaned_data['schoolclasses']

        # Sets the User and Student fields to the new values
        account.username = username
        account.pin = pin
        account.save()

        person.fullname = fullname
        person.schoolyear = schoolyear
        person.save()

        # Clears, then creates relationships between other tables
        old_parents = Parent.objects.filter(children=person)
        for parent in old_parents:
            parent.children.remove(person)

        for parent in parents:
            parent.children.add(person)

        old_schoolclasses = SchoolClass.objects.filter(students=person)
        for schoolclass in old_schoolclasses:
            schoolclass.students.remove(person)

        for schoolclass in schoolclasses:
            schoolclass.students.add(person)

    def edit_parent(self, account, person, cleaned_data, username, pin):

        # Gets contents of remaining fields
        fullname = cleaned_data['fullname']
        children = cleaned_data['children']

        # Sets the User and Parent fields to the new values
        account.username = username
        account.pin = pin
        account.save()

        person.fullname = fullname
        person.save()

        # Clears, then creates relationships between other tables
        person.children.clear()
        for child in children:
            person.children.add(child)

    def edit_teacher(self, account, person, cleaned_data, username, pin):

        # Gets contents of remaining fields
        fullname = cleaned_data['fullname']
        title = cleaned_data['title']
        subject = cleaned_data['subject']
        schoolclasses = cleaned_data['schoolclasses']

        # Sets the User and Teacher fields to the new values
        account.username = username
        account.pin = pin
        account.save()

        person.fullname = fullname
        person.title = title
        person.subject = subject
        person.save()

        # Clears, then creates relationships between other tables
        old_schoolclasses = SchoolClass.objects.filter(teachers=person)
        for schoolclass in old_schoolclasses:
            schoolclass.teachers.remove(person)

        for schoolclass in schoolclasses:
            schoolclass.teachers.add(person)

    def edit_admin(self, account, person, cleaned_data, username, pin):

        # Gets contents of remaining fields
        fullname = cleaned_data['fullname']

        # Sets the User and Admin fields to the new values
        account.username = username
        account.pin = pin
        account.save()

        person.fullname = fullname
        person.save()

class DeleteAccountView(RedirectView):

    def get(self, request, account_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Checks if id passed in the URL corresponds to account
                    # Gets the account
                    accounts = User.objects.filter(id=account_id)
                    if len(accounts) == 1:
                        account = accounts[0]

                        # Deletes account record
                        account.delete()

                        # Redirect to Accounts page
                        return redirect('admin:accounts')
                    else:
                        return redirect('admin:accounts')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class ClassesView(TemplateView):
    template_name = 'admin/classes.html'

    def get(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Creates the dictionary to be passed to the template
                    # Gets all classes
                    args = {'username': user.username}
                    args['schoolclasses'] = SchoolClass.objects.all()

                    # Renders template
                    return render(request, self.template_name, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class AddClassView(TemplateView):
    template_name = 'admin/class.html'

    def get(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]
                    form = forms.ClassForm()

                    # Creates the dictionary to be passed to the template
                    args = {'username': user.username, 'mode': 'Add', 'form': form}

                    # Renders template
                    return render(request, self.template_name, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def post(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]
                    form = forms.ClassForm(request.POST)

                    # Creates the dictionary to be passed to the template
                    args = {'username': user.username, 'mode': 'Add', 'form': form}

                    return self.process_form(request, form, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def process_form(self, request, form, args):

        # Checks if form is valid
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the contents of all the fields
            cleaned_data = form.cleaned_data
            classname = cleaned_data['classname']
            subject = cleaned_data['subject']
            schoolyear = cleaned_data['schoolyear']
            students = cleaned_data['students']
            teachers = cleaned_data['teachers']
            pes = cleaned_data['pes']
            details = cleaned_data['details']

            # Creates SchoolClass record
            newschoolclass = SchoolClass(classname=classname, subject=subject, schoolyear=schoolyear, details=details)
            newschoolclass.save()

            # Creates relationships between other tables
            for student in students:
                newschoolclass.students.add(student)

            for teacher in teachers:
                newschoolclass.teachers.add(teacher)

            for pe in pes:
                pe.schoolclasses.add(newschoolclass)

            # Redirects back to Classes page
            return redirect('admin:classes')
        else:
            args['error_message'] = '× Something went wrong, please try again.'
            return render(request, self.template_name, args)

class EditClassView(TemplateView):
    template_name = 'admin/class.html'

    def get(self, request, class_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Checks if id passed in the URL corresponds to a class
                    # Gets the class
                    schoolclasses = SchoolClass.objects.filter(id=class_id)
                    if len(schoolclasses) == 1:
                        schoolclass = schoolclasses[0]

                        # Creates and populates a ClassForm with the class' details
                        form = forms.ClassForm(initial={'classname': schoolclass.classname,
                                                        'subject': schoolclass.subject,
                                                        'schoolyear': schoolclass.schoolyear,
                                                        'students': Student.objects.filter(schoolclass=schoolclass),
                                                        'teachers': Teacher.objects.filter(schoolclass=schoolclass),
                                                        'pes': ParentsEvening.objects.filter(schoolclasses=schoolclass),
                                                        'details': schoolclass.details})


                        # Creates the dictionary to be passed to the template
                        args = {'username': user.username, 'mode': 'Edit', 'class_id': class_id, 'form': form}

                        # Renders template
                        return render(request, self.template_name, args)
                    else:
                        return redirect('admin:classes')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def post(self, request, class_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Checks if id passed in the URL corresponds to a class
                    # Gets the class
                    schoolclasses = SchoolClass.objects.filter(id=class_id)
                    if len(schoolclasses) == 1:
                        schoolclass = schoolclasses[0]

                        form = forms.ClassForm(request.POST)

                        # Creates the dictionary to be passed to the template
                        args = {'username': user.username, 'mode': 'Edit', 'class_id': class_id, 'form': form}

                        return self.process_form(request, schoolclass, form, args)
                    else:
                        return redirect('admin:classes')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def process_form(self, request, schoolclass, form, args):

        # Checks if form is valid
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the contents of all the fields
            cleaned_data = form.cleaned_data
            classname = cleaned_data['classname']
            subject = cleaned_data['subject']
            schoolyear = cleaned_data['schoolyear']
            students = cleaned_data['students']
            teachers = cleaned_data['teachers']
            pes = cleaned_data['pes']
            details = cleaned_data['details']

            # Sets the SchooClass fields to the new values
            schoolclass.classname = classname
            schoolclass.subject = subject
            schoolclass.schoolyear = schoolyear
            schoolclass.details = details
            schoolclass.save()

            # Clears, then creates relationships between other tables
            schoolclass.students.clear()
            for student in students:
                schoolclass.students.add(student)

            schoolclass.teachers.clear()
            for teacher in teachers:
                schoolclass.teachers.add(teacher)

            old_pes = ParentsEvening.objects.filter(schoolclasses=schoolclass)
            for pe in old_pes:
                pe.schoolclasses.remove(schoolclass)

            for pe in pes:
                pe.schoolclasses.add(schoolclass)

            # Redirects back to Classes page
            return redirect('admin:classes')
        else:
            args['error_message'] = '× Something went wrong, please try again.'
            return render(request, self.template_name, args)

class DeleteClassView(RedirectView):

    def get(self, request, class_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Checks if id passed in the URL corresponds to a class
                    # Gets the class
                    schoolclasses = SchoolClass.objects.filter(id=class_id)
                    if len(schoolclasses) == 1:
                        schoolclass = schoolclasses[0]

                        # Deletes SchoolClass record
                        schoolclass.delete()

                        # Redirects back to Classes page
                        return redirect('admin:classes')
                    else:
                        return redirect('admin:classes')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class ParentsEveningsView(TemplateView):
    template_name = 'admin/parentsevenings.html'

    def get(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Creates the dictionary to be passed to the template
                    # Gets all parents' evenings
                    args = {'username': user.username}
                    args['pes'] = ParentsEvening.objects.all()

                    # Renders template
                    return render(request, self.template_name, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class AddParentsEveningView(TemplateView):
    template_name = 'admin/parentsevening.html'

    def get(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]
                    form = forms.ParentsEveningForm()

                    # Creates the dictionary to be passed to the template
                    args = {'username': user.username, 'mode': 'Add', 'form': form}

                    # Renders template
                    return render(request, self.template_name, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def post(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]
                    form = forms.ParentsEveningForm(request.POST)

                    # Creates the dictionary to be passed to the template
                    args = {'username': user.username, 'mode': 'Add', 'form': form}

                    return self.process_form(request, form, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def process_form(self, request, form, args):

        # Checks if form is valid
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the contents of all the fields
            cleaned_data = form.cleaned_data
            pename = cleaned_data['pename']
            date = cleaned_data['date']
            starttime = cleaned_data['starttime']
            endtime = cleaned_data['endtime']
            appointmentlength = cleaned_data['appointmentlength']
            schoolclasses = cleaned_data['schoolclasses']
            details = cleaned_data['details']

            # Creates ParentsEvening record
            newpe = ParentsEvening(pename=pename, date=date, starttime=starttime, endtime=endtime, appointmentlength=appointmentlength, details=details)
            newpe.save()

            # Creates relationships between other tables
            for schoolclass in schoolclasses:
                newpe.schoolclasses.add(schoolclass)

            # Redirects back to ParentsEvenings page
            return redirect('admin:parentsevenings')

        else:
            args['error_message'] = '× Something went wrong, please try again.'
            return render(request, self.template_name, args)

class EditParentsEveningView(TemplateView):
    template_name = 'admin/parentsevening.html'

    def get(self, request, pe_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Checks if id passed in the URL corresponds to a parents' evening
                    # Gets the parents' evening
                    pes = ParentsEvening.objects.filter(id=pe_id)
                    if len(pes) == 1:
                        pe = pes[0]

                        # Converts the date field into a string
                        # Creates and populates a ParentsEveningForm
                        str_date = str(pe.date)
                        form = forms.ParentsEveningForm(initial={'pename': pe.pename,
                                                                 'date': str_date[8:10]+'/'+str_date[5:7]+'/'+str_date[0:4],
                                                                 'starttime': str(pe.starttime)[0:5],
                                                                 'endtime': str(pe.endtime)[0:5],
                                                                 'appointmentlength': str(pe.appointmentlength)[0:5],
                                                                 'schoolclasses': SchoolClass.objects.filter(parentsevening=pe),
                                                                 'details': pe.details})

                        # Creates the dictionary to be passed to the template
                        args = {'username': user.username, 'mode': 'Edit', 'pe_id': pe_id, 'form': form}

                        # Renders template
                        return render(request, self.template_name, args)
                    else:
                        return redirect('admin:parentsevenings')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def post(self, request, pe_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Checks if id passed in the URL corresponds to a parents' evening
                    # Gets the parents' evening
                    pes = ParentsEvening.objects.filter(id=pe_id)
                    if len(pes) == 1:
                        pe = pes[0]
                        form = forms.ParentsEveningForm(request.POST)

                        # Creates the dictionary to be passed to the template
                        args = {'username': user.username, 'mode': 'Edit', 'pe_id': pe_id, 'form': form}

                        return self.process_form(request, pe, form, args)
                    else:
                        return redirect('admin:parentsevenings')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def process_form(self, request, pe, form, args):

        # Checks if form is valid
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the contents of all the fields
            cleaned_data = form.cleaned_data
            pename = cleaned_data['pename']
            date = cleaned_data['date']
            starttime = cleaned_data['starttime']
            endtime = cleaned_data['endtime']
            appointmentlength = cleaned_data['appointmentlength']
            schoolclasses = cleaned_data['schoolclasses']
            details = cleaned_data['details']

            # Sets the ParentsEvening fields to the new values
            pe.pename = pename
            pe.date = date
            pe.starttime = starttime
            pe.endtime = endtime
            pe.appointmentlength = appointmentlength
            pe.details = details
            pe.save()

            # Clears, then creates relationships between other tables
            pe.schoolclasses.clear()
            for schoolclass in schoolclasses:
                pe.schoolclasses.add(schoolclass)

            # Redirect back to ParentsEvenings page
            return redirect('admin:parentsevenings')

        else:
            args['error_message'] = '× Something went wrong, please try again.'
            return render(request, self.template_name, args)

class DeleteParentsEveningView(RedirectView):

    def get(self, request, pe_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Admin":

                # Checks user's account only corresponds to one person
                # Gets the current person
                admins = Admin.objects.filter(user=user)
                if len(admins) == 1:
                    admin = admins[0]

                    # Checks if id passed in the URL corresponds to a parents' evening
                    # Gets the parents' evening
                    pes = ParentsEvening.objects.filter(id=pe_id)
                    if len(pes) == 1:
                        pe = pes[0]

                        # Deletes ParentsEvening record
                        pe.delete()

                        # Redirects back to ParentsEvenings page
                        return redirect('admin:parentsevenings')
                    else:
                        return redirect('admin:parentsevenings')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')
