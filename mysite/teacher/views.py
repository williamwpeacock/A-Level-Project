import datetime

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.db.models import Q

from . import forms
from pebookingsystem.models import *
from pebookingsystem import functions

class WelcomeView(TemplateView):
    template_name = 'teacher/welcome.html'

    def get(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Teacher":

                # Checks user's account only corresponds to one person
                # Gets the current person
                teachers = Teacher.objects.filter(user=user)
                if len(teachers) == 1:
                    teacher = teachers[0]

                    # Creates the dictionary to be passed to the template
                    # Gets all parents' evenings applicable to this person
                    # Gets this person's bookings
                    args = {'username': user.username, 'fullname': teacher.fullname, 'role': user.role}
                    args['pes'] = ParentsEvening.objects.filter(schoolclasses__teachers=teacher).values('id', 'pename').distinct()
                    args['bookings'] = PEBooking.objects.filter(schoolclass__teachers=teacher).values('parentsevening__pename', 'schoolclass__classname', 'student__fullname', 'parentsevening__date', 'timeslot').order_by('parentsevening__date', 'timeslot')

                    # Renders template
                    return render(request, self.template_name, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class ParentsEveningView(TemplateView):
    template_name = 'teacher/parentsevening.html'

    def get(self, request, pe_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Teacher":

                # Checks user's account only corresponds to one person
                # Gets the current person
                teachers = Teacher.objects.filter(user=user)
                if len(teachers) == 1:
                    teacher = teachers[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__teachers=teacher)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Creates the dictionary to be passed to the template
                        # Gets all classes applicable to this person and parentsevening
                        # Gets this person's bookings in this parents' evening
                        args = {'username': user.username, 'role': user.role, 'pe': pe}
                        args['schoolclasses'] = SchoolClass.objects.filter(Q(teachers=teacher) & Q(parentsevening=pe)).values('id', 'classname')
                        args['bookings'] = PEBooking.objects.filter(Q(schoolclass__teachers=teacher) & Q(parentsevening=pe)).values('schoolclass__classname', 'student__fullname', 'parentsevening__date', 'timeslot').order_by('parentsevening__date', 'timeslot')

                        # Renders template
                        return render(request, self.template_name, args)
                    else:
                        return redirect('teacher:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class ClassView(TemplateView):
    template_name = 'teacher/class.html'

    def get(self, request, pe_id, class_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Teacher":

                # Checks user's account only corresponds to one person
                # Gets the current person
                teachers = Teacher.objects.filter(user=user)
                if len(teachers) == 1:
                    teacher = teachers[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__teachers=teacher)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(teachers=teacher) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Creates the dictionary to be passed to the template
                            # Gets all classes applicable to this person and parentsevening
                            args = {'username': user.username, 'role': user.role, 'pe': pe, 'schoolclass': schoolclass}
                            args['schoolclasses'] = SchoolClass.objects.filter(Q(teachers=teacher) & Q(parentsevening=pe)).values('id', 'classname')

                            # Gets this class' bookings table
                            args['bookings'] = self.get_bookings(pe, schoolclass)

                            # Renders template
                            return render(request, self.template_name, args)
                        else:
                            return redirect('teacher:parentsevening', pe_id)
                    else:
                        return redirect('teacher:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def get_bookings(self, pe, schoolclass):

        # Get teacher conflicts and bookings for this class
        teacher_conflicts = functions.get_teacher_conflicts(pe, schoolclass)
        class_conflicts = self.get_class_bookings(pe, schoolclass)

        bookings = []

        # Convert parents' evening times to 'timedelta' so calculations can be performed with them
        starttime = datetime.timedelta(hours=pe.starttime.hour, minutes=pe.starttime.minute, seconds=0)
        appointmentlength = datetime.timedelta(hours=pe.appointmentlength.hour, minutes=pe.appointmentlength.minute, seconds=0)
        endtime = datetime.timedelta(hours=pe.endtime.hour, minutes=pe.endtime.minute, seconds=0)

        # Loops through each timeslot
        timeslot = starttime
        while timeslot < endtime:

            # Converts timeslot into a form to be displayed
            timeslot_str_full = str(timeslot)
            if len(timeslot_str_full)%2 == 0:
                timeslot_str = timeslot_str_full[0]+timeslot_str_full[1]+":"+timeslot_str_full[3]+timeslot_str_full[4]
            else:
                timeslot_str = "0"+timeslot_str_full[0]+":"+timeslot_str_full[2]+timeslot_str_full[3]

            row = [timeslot_str]

            # Check if this timeslot is available for any teachers
            teachers_available = True
            if timeslot in teacher_conflicts:
                teachers_available = False

            # Check if this timeslot is available for this student and, if not, if this booking is their's
            class_available = True
            for booking in class_conflicts:
                if timeslot == booking[0]:
                    class_available = False
                    student_conflict_name = booking[1].fullname

            # Fill the rows with the data: [timeslot, teacher availability, student conflicts, action, timeslot_url]
            if teachers_available:
                row.append("Available")
            else:
                row.append("Not available")

            if class_available:
                row.append("None")
                if teachers_available:
                    row.append("book")
                    row.append(timeslot_str[0]+timeslot_str[1]+timeslot_str[3]+timeslot_str[4])
                else:
                    row.append("")
            else:
                row.append(student_conflict_name)
                row.append("view")
                row.append(timeslot_str[0]+timeslot_str[1]+timeslot_str[3]+timeslot_str[4])

            # Append the current row to the final list and move on to the next timeslot
            bookings.append(row)
            timeslot += appointmentlength

        return bookings

    def get_class_bookings(self, pe, schoolclass):
        class_bookings = []
        all_bookings = PEBooking.objects.filter(Q(parentsevening=pe) & Q(schoolclass=schoolclass))

        # Adds timeslot and student name for all bookings to class_bookings
        # Converts timeslot to 'timedelta' so calculations can be performed
        for booking in all_bookings:
            class_bookings.append([datetime.timedelta(hours=booking.timeslot.hour, minutes=booking.timeslot.minute, seconds=0), booking.student])

        return class_bookings

class BookView(TemplateView):
    template_name = 'teacher/book.html'

    def get(self, request, pe_id, class_id, timeslot):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Teacher":

                # Checks user's account only corresponds to one person
                # Gets the current person
                teachers = Teacher.objects.filter(user=user)
                if len(teachers) == 1:
                    teacher = teachers[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__teachers=teacher)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(teachers=teacher) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Converts the timeslot in the url to a 'timedelta' object
                            # Checks if the current timeslot is free for this class in this parents' evening
                            urltotime = datetime.timedelta(hours=int(timeslot[0]+timeslot[1]), minutes=int(timeslot[2]+timeslot[3]), seconds=0)
                            if self.time_free(urltotime, pe, schoolclass):

                                # Converts the timeslot in the url to a 'time' object
                                # Gets all the students' ids who have a booking in this parents' evening either in this timeslot or this class
                                # Gets all the students' in this class who are available for this timeslot
                                time = datetime.time(int(timeslot[0]+timeslot[1]), int(timeslot[2]+timeslot[3]), 0)
                                students_with_bookings = PEBooking.objects.filter(Q(parentsevening=pe) & Q(Q(timeslot=time) | Q(schoolclass=schoolclass))).values('student__id')
                                students = Student.objects.filter(Q(schoolclass=schoolclass) & ~Q(id__in=students_with_bookings))

                                form = forms.BookForm(students=students)

                                # Creates the dictionary to be passed to the template
                                # Passes a displayable timeslot to the dictionary
                                # Gets all classes applicable to this person and parentsevening
                                args = {'username': user.username, 'role': user.role, 'pe': pe, 'schoolclass': schoolclass, 'students': students, 'form': form}
                                args['timeslot'] = timeslot[0]+timeslot[1]+":"+timeslot[2]+timeslot[3]
                                args['schoolclasses'] = SchoolClass.objects.filter(Q(teachers=teacher) & Q(parentsevening=pe)).values('id', 'subject')

                                # Renders template
                                return render(request, self.template_name, args)
                            else:
                                return redirect('teacher:class', pe_id, class_id)
                        else:
                            return redirect('teacher:parentsevening', pe_id)
                    else:
                        return redirect('teacher:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def post(self, request, pe_id, class_id, timeslot):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Teacher":

                # Checks user's account only corresponds to one person
                # Gets the current person
                teachers = Teacher.objects.filter(user=user)
                if len(teachers) == 1:
                    teacher = teachers[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__teachers=teacher)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(teachers=teacher) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Converts the timeslot in the url to a 'timedelta' object
                            # Checks if the current timeslot is free for this class in this parents' evening
                            urltotime = datetime.timedelta(hours=int(timeslot[0]+timeslot[1]), minutes=int(timeslot[2]+timeslot[3]), seconds=0)
                            if self.time_free(urltotime, pe, schoolclass):

                                # Converts the timeslot in the url to a 'time' object
                                # Gets all the students' ids who have a booking in this parents' evening either in this timeslot or this class
                                # Gets all the students' in this class who are available for this timeslot
                                time = datetime.time(int(timeslot[0]+timeslot[1]), int(timeslot[2]+timeslot[3]), 0)
                                students_with_bookings = PEBooking.objects.filter(Q(parentsevening=pe) & Q(Q(timeslot=time) | Q(schoolclass=schoolclass))).values('student__id')
                                students = Student.objects.filter(Q(schoolclass=schoolclass) & ~Q(id__in=students_with_bookings))

                                form = forms.BookForm(request.POST, students=students)

                                # Creates the dictionary to be passed to the template
                                # Passes a displayable timeslot to the dictionary
                                # Gets all classes applicable to this person and parentsevening
                                args = {'username': user.username, 'role': user.role, 'pe': pe, 'schoolclass': schoolclass, 'students': students, 'form': form}
                                args['timeslot'] = timeslot[0]+timeslot[1]+":"+timeslot[2]+timeslot[3]
                                args['schoolclasses'] = SchoolClass.objects.filter(Q(teachers=teacher) & Q(parentsevening=pe)).values('id', 'subject')

                                return self.process_form(request, pe, schoolclass, urltotime, form, args)
                            else:
                                return redirect('teacher:class', pe_id, class_id)
                        else:
                            return redirect('teacher:parentsevening', pe_id)
                    else:
                        return redirect('teacher:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def time_free(self, current_timeslot, pe, schoolclass):

        # Convert parents' evening times to 'timedelta' so calculations can be performed with them
        starttime = datetime.timedelta(hours=pe.starttime.hour, minutes=pe.starttime.minute, seconds=0)
        appointmentlength = datetime.timedelta(hours=pe.appointmentlength.hour, minutes=pe.appointmentlength.minute, seconds=0)
        endtime = datetime.timedelta(hours=pe.endtime.hour, minutes=pe.endtime.minute, seconds=0)

        # Loops through each timeslot
        timeslot = starttime
        while timeslot < endtime:
            if timeslot == current_timeslot:

                # Get all conflicts for this booking
                teacher_conflicts = functions.get_teacher_conflicts(pe, schoolclass)
                class_conflicts = self.get_class_conflicts(pe, schoolclass)
                all_conflicts = teacher_conflicts + class_conflicts

                # Check if current timeslot conflicts with an existing booking
                if current_timeslot in all_conflicts:
                    return False
                else:
                    return True
            else:
                timeslot += appointmentlength

        return False

    def get_class_conflicts(self, pe, schoolclass):
        class_bookings = []
        all_bookings = PEBooking.objects.filter(Q(parentsevening=pe) & Q(schoolclass=schoolclass))

        # Adds timeslot for all bookings to class_bookings
        # Converts timeslot to 'timedelta' so calculations can be performed
        for booking in all_bookings:
            class_bookings.append(datetime.timedelta(hours=booking.timeslot.hour, minutes=booking.timeslot.minute, seconds=0))

        return class_bookings

    def process_form(self, request, pe, schoolclass, timeslot, form, args):

        # Convert the 'timedelta' object into a 'time' object so it can be passed into a Django 'TimeField'
        hours = (timeslot.seconds // 60) // 60
        minutes = (timeslot.seconds // 60) % 60
        seconds = timeslot.seconds % 60
        time = datetime.time(hours, minutes, seconds)

        # Checks if form is valid
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the 'notes' and 'student' fields
            cleaned_data = form.cleaned_data
            notes = cleaned_data['notes']
            student = cleaned_data['student']

            # Checks if 'notes' is empty, if so, creates booking with 'None' in the notes field
            # If not, creates booking with 'notes' in the notes field
            if notes != '':
                PEBooking.objects.create(parentsevening=pe, schoolclass=schoolclass, student=student, timeslot=time, notes=notes)
            else:
                PEBooking.objects.create(parentsevening=pe, schoolclass=schoolclass, student=student, timeslot=time, notes='None')

            # Redirects back to Class page
            return redirect('teacher:class', pe.id, schoolclass.id)
        else:
            args['error_message'] = '× Something went wrong, please try again.'
            return render(request, self.template_name, args)

class ViewBookingView(TemplateView):
    template_name = 'teacher/viewbooking.html'

    def get(self, request, pe_id, class_id, timeslot):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Teacher":

                # Checks user's account only corresponds to one person
                # Gets the current person
                teachers = Teacher.objects.filter(user=user)
                if len(teachers) == 1:
                    teacher = teachers[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__teachers=teacher)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(teachers=teacher) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Converts the timeslot in the url to a 'time' object
                            # Catches error if an invalid timeslot is given in the url
                            try:
                                urltotime = datetime.time(int(timeslot[0]+timeslot[1]), int(timeslot[2]+timeslot[3]), 0)
                            except ValueError:
                                return redirect('teacher:class', pe_id, class_id)

                            # Checks if the current timeslot is booked for this class in this parents' evening
                            # Gets the booking
                            bookings = PEBooking.objects.filter(Q(parentsevening=pe) & Q(schoolclass=schoolclass) & Q(timeslot=urltotime))
                            if len(bookings) == 1:
                                booking = bookings[0]

                                # Creates the dictionary to be passed to the template
                                # Passes a displayable timeslot to the dictionary
                                # Gets all classes applicable to this person and parentsevening
                                args = {'username': user.username, 'role': user.role, 'pe': pe, 'schoolclass': schoolclass, 'student': booking.student.fullname, 'notes': booking.notes, 'urltimeslot': timeslot}
                                args['timeslot'] = timeslot[0]+timeslot[1]+":"+timeslot[2]+timeslot[3]
                                args['schoolclasses'] = SchoolClass.objects.filter(Q(teachers=teacher) & Q(parentsevening=pe)).values('id', 'subject')

                                # Renders template
                                return render(request, self.template_name, args)
                            else:
                                return redirect('teacher:class', pe_id, class_id)
                        else:
                            return redirect('teacher:parentsevening', pe_id)
                    else:
                        return redirect('teacher:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class RemoveBookingView(RedirectView):

    def get(self, request, pe_id, class_id, timeslot):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Teacher":

                # Checks user's account only corresponds to one person
                # Gets the current person
                teachers = Teacher.objects.filter(user=user)
                if len(teachers) == 1:
                    teacher = teachers[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__teachers=teacher)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(teachers=teacher) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Converts the timeslot in the url to a 'time' object
                            # Catches error if an invalid timeslot is given in the url
                            try:
                                urltotime = datetime.time(int(timeslot[0]+timeslot[1]), int(timeslot[2]+timeslot[3]), 0)
                            except ValueError:
                                return redirect('teacher:class', pe_id, class_id)

                            # Checks if the current timeslot is booked for this class in this parents' evening
                            # Gets the booking
                            bookings = PEBooking.objects.filter(Q(parentsevening=pe) & Q(schoolclass=schoolclass) & Q(timeslot=urltotime))
                            if len(bookings) == 1:
                                booking = bookings[0]

                                # Deletes booking record
                                booking.delete()

                                # Redirects back to Class page
                                return redirect('teacher:class', pe_id, class_id)
                            else:
                                return redirect('teacher:class', pe_id, class_id)
                        else:
                            return redirect('teacher:parentsevening', pe_id)
                    else:
                        return redirect('teacher:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')
