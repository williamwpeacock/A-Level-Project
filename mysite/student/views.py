import datetime

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.db.models import Q

from . import forms
from pebookingsystem.models import *
from pebookingsystem import functions

class WelcomeView(TemplateView):
    template_name = 'student/welcome.html'

    def get(self, request):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            #Checks user is correct role
            if user.role == "Student":

                # Checks user's account only corresponds to one person
                # Gets the current person
                students = Student.objects.filter(user=user)
                if len(students) == 1:
                    student = students[0]

                    # Creates the dictionary to be passed to the template
                    # Gets all parents' evenings applicable to this person
                    # Gets this person's bookings
                    args = {'username': user.username, 'fullname': student.fullname, 'role': user.role}
                    args['pes'] = ParentsEvening.objects.filter(schoolclasses__students=student).values('id', 'pename').distinct()
                    args['bookings'] = PEBooking.objects.filter(student=student).values('parentsevening__pename', 'schoolclass__subject', 'parentsevening__date', 'timeslot').order_by('parentsevening__date', 'timeslot')

                    # Renders template
                    return render(request, self.template_name, args)
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class ParentsEveningView(TemplateView):
    template_name = 'student/parentsevening.html'

    def get(self, request, pe_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            # Checks user is correct role
            if user.role == "Student":

                # Checks user's account only corresponds to one person
                # Gets the current person
                students = Student.objects.filter(user=user)
                if len(students) == 1:
                    student = students[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__students=student)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Creates the dictionary to be passed to the template
                        # Gets all classes applicable to this person and parentsevening
                        # Gets this person's bookings in this parents' evening
                        args = {'username': user.username, 'role': user.role, 'pe': pe}
                        args['schoolclasses'] = SchoolClass.objects.filter(Q(students=student) & Q(parentsevening=pe)).values('id', 'subject')
                        args['bookings'] = PEBooking.objects.filter(Q(student=student) & Q(parentsevening=pe)).values('schoolclass__subject', 'parentsevening__date', 'timeslot').order_by('parentsevening__date', 'timeslot')

                        # Renders template
                        return render(request, self.template_name, args)
                    else:
                        return redirect('student:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

class ClassView(TemplateView):
    template_name = 'student/class.html'

    def get(self, request, pe_id, class_id):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            # Checks user is correct role
            if user.role == "Student":

                # Checks user's account only corresponds to one person
                # Gets the current person
                students = Student.objects.filter(user=user)
                if len(students) == 1:
                    student = students[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__students=student)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(students=student) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Creates the dictionary to be passed to the template
                            # Gets all classes applicable to this person and parentsevening
                            args = {'username': user.username, 'role': user.role, 'pe': pe, 'schoolclass': schoolclass}
                            args['schoolclasses'] = SchoolClass.objects.filter(Q(students=student) & Q(parentsevening=pe)).values('id', 'subject')

                            # Gets this class' bookings table
                            args['bookings'] = self.get_bookings(pe, schoolclass, student)

                            # Renders template
                            return render(request, self.template_name, args)
                        else:
                            return redirect('student:parentsevening', pe_id)
                    else:
                        return redirect('student:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def get_bookings(self, pe, schoolclass, student):

        # Get teacher conflicts, student conflicts, and student booking(s) for this class
        teacher_conflicts = functions.get_teacher_conflicts(pe, schoolclass)
        my_conflicts = self.get_my_conflicts(pe, student)

        # Check if this student has a booking for this class and parentsevening
        my_booking = PEBooking.objects.filter(Q(parentsevening=pe) & Q(schoolclass=schoolclass) & Q(student=student))
        my_booking_exists = False
        if len(my_booking) != 0:
            my_booking_exists = True

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
            student_available = True
            my_booking = False
            for booking in my_conflicts:
                if timeslot == booking[0]:
                    student_available = False
                    student_conflict_subject = booking[1].subject
                    if booking[1] == schoolclass:
                        my_booking = True

            # Fill the rows with the data: [timeslot, teacher availability, student conflicts, action, timeslot_url]
            if teachers_available:
                row.append("Available")
            else:
                row.append("Not available")

            if student_available:
                row.append("None")
                if my_booking_exists:
                    row.append("")
                else:
                    if teachers_available:
                        row.append("book")
                        row.append(timeslot_str[0]+timeslot_str[1]+timeslot_str[3]+timeslot_str[4])
                    else:
                        row.append("")
            else:
                row.append(student_conflict_subject)
                if my_booking_exists:
                    if my_booking:
                        row.append("view")
                        row.append(timeslot_str[0]+timeslot_str[1]+timeslot_str[3]+timeslot_str[4])
                    else:
                        row.append("")
                else:
                    row.append("")

            # Append the current row to the final list and move on to the next timeslot
            bookings.append(row)
            timeslot += appointmentlength

        return bookings

    def get_my_conflicts(self, pe, student):
        conflicts = []
        all_bookings = PEBooking.objects.filter(Q(parentsevening=pe) & Q(student=student))

        # Adds timeslot and class for all bookings to conflicts
        # Converts timeslot to 'timedelta' so calculations can be performed
        for booking in all_bookings:
            conflicts.append([datetime.timedelta(hours=booking.timeslot.hour, minutes=booking.timeslot.minute, seconds=0), booking.schoolclass])

        return conflicts

class BookView(TemplateView):
    template_name = 'student/book.html'

    def get(self, request, pe_id, class_id, timeslot):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            # Checks user is correct role
            if user.role == "Student":

                # Checks user's account only corresponds to one person
                # Gets the current person
                students = Student.objects.filter(user=user)
                if len(students) == 1:
                    student = students[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__students=student)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(students=student) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Converts the timeslot in the url to a 'timedelta' object
                            # Checks if the current timeslot is free for this student for this class in this parents' evening
                            urltotime = datetime.timedelta(hours=int(timeslot[0]+timeslot[1]), minutes=int(timeslot[2]+timeslot[3]), seconds=0)
                            if self.time_free(urltotime, pe, schoolclass, student):
                                form = forms.BookForm()

                                # Creates the dictionary to be passed to the template
                                # Passes a displayable timeslot to the dictionary
                                # Gets all classes applicable to this person and parentsevening
                                args = {'username': user.username, 'role': user.role, 'pe': pe, 'schoolclass': schoolclass, 'form': form}
                                args['timeslot'] = timeslot[0]+timeslot[1]+":"+timeslot[2]+timeslot[3]
                                args['schoolclasses'] = SchoolClass.objects.filter(Q(students=student) & Q(parentsevening=pe)).values('id', 'subject')

                                # Renders template
                                return render(request, self.template_name, args)
                            else:
                                return redirect('student:class', pe_id, class_id)
                        else:
                            return redirect('student:parentsevening', pe_id)
                    else:
                        return redirect('student:welcome')
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

            # Checks user is correct role
            if user.role == "Student":

                # Checks user's account only corresponds to one person
                # Gets the current person
                students = Student.objects.filter(user=user)
                if len(students) == 1:
                    student = students[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__students=student)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(students=student) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Converts the timeslot in the url to a 'timedelta' object
                            # Checks if the current timeslot is free for this student for this class in this parents' evening
                            urltotime = datetime.timedelta(hours=int(timeslot[0]+timeslot[1]), minutes=int(timeslot[2]+timeslot[3]), seconds=0)
                            if self.time_free(urltotime, pe, schoolclass, student):
                                form = forms.BookForm(request.POST)

                                # Creates the dictionary to be passed to the template
                                # Passes a displayable timeslot to the dictionary
                                # Gets all classes applicable to this person and parentsevening
                                args = {'username': user.username, 'role': user.role, 'pe': pe, 'schoolclass': schoolclass, 'form': form}
                                args['timeslot'] = timeslot[0]+timeslot[1]+":"+timeslot[2]+timeslot[3]
                                args['schoolclasses'] = SchoolClass.objects.filter(Q(students=student) & Q(parentsevening=pe)).values('id', 'subject')

                                return self.process_form(request, pe, schoolclass, student, urltotime, form, args)
                            else:
                                return redirect('student:class', pe_id, class_id)
                        else:
                            return redirect('student:parentsevening', pe_id)
                    else:
                        return redirect('student:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def time_free(self, current_timeslot, pe, schoolclass, student):

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
                my_conflicts = self.get_my_conflicts(pe, student)
                all_conflicts = teacher_conflicts + my_conflicts

                # Check if current timeslot conflicts with an existing booking
                if current_timeslot in all_conflicts:
                    return False

                # Check if this person already has a booking
                booked_by_me = PEBooking.objects.filter(Q(parentsevening=pe) & Q(schoolclass=schoolclass) & Q(student=student))
                if len(booked_by_me) == 0:
                    return True
                else:
                    return False
            else:
                timeslot += appointmentlength

        return False

    def get_my_conflicts(self, pe, student):
        conflicts = []
        all_bookings = PEBooking.objects.filter(Q(parentsevening=pe) & Q(student=student))

        # Adds timeslot for all bookings to conflicts
        # Converts timeslot to 'timedelta' so calculations can be performed
        for booking in all_bookings:
            conflicts.append(datetime.timedelta(hours=booking.timeslot.hour, minutes=booking.timeslot.minute, seconds=0))

        return conflicts

    def process_form(self, request, pe, schoolclass, student, timeslot, form, args):

        # Convert the 'timedelta' object into a 'time' object so it can be passed into a Django 'TimeField'
        hours = (timeslot.seconds // 60) // 60
        minutes = (timeslot.seconds // 60) % 60
        seconds = timeslot.seconds % 60
        time = datetime.time(hours, minutes, seconds)

        # Checks if form is valid
        if form.is_valid():

            # Extracts cleaned data from the form
            # Gets the 'notes' field
            cleaned_data = form.cleaned_data
            notes = cleaned_data['notes']

            # Checks if 'notes' is empty, if so, creates booking with 'None' in the notes field
            # If not, creates booking with 'notes' in the notes field
            if notes != '':
                PEBooking.objects.create(parentsevening=pe, schoolclass=schoolclass, student=student, timeslot=time, notes=notes)
            else:
                PEBooking.objects.create(parentsevening=pe, schoolclass=schoolclass, student=student, timeslot=time, notes='None')

            # Redirects back to Class page
            return redirect('student:class', pe.id, schoolclass.id)
        else:
            args['error_message'] = '× Something went wrong, please try again.'
            return render(request, self.template_name, args)

class ViewBookingView(TemplateView):
    template_name = 'student/viewbooking.html'

    def get(self, request, pe_id, class_id, timeslot):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            # Checks user is correct role
            if user.role == "Student":

                # Checks user's account only corresponds to one person
                # Gets the current person
                students = Student.objects.filter(user=user)
                if len(students) == 1:
                    student = students[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__students=student)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(students=student) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Converts the timeslot in the url to a 'time' object
                            # Catches error if an invalid timeslot is given in the url
                            try:
                                urltotime = datetime.time(int(timeslot[0]+timeslot[1]), int(timeslot[2]+timeslot[3]), 0)
                            except ValueError:
                                return redirect('student:class', pe_id, class_id)

                            # Checks if the current timeslot is booked by this student for this class in this parents' evening
                            # Gets the booking
                            booked_by_me = PEBooking.objects.filter(Q(parentsevening=pe) & Q(schoolclass=schoolclass) & Q(student=student))
                            if self.time_booked(urltotime, booked_by_me):
                                booking = booked_by_me[0]

                                # Creates the dictionary to be passed to the template
                                # Passes a displayable timeslot to the dictionary
                                # Gets all classes applicable to this person and parentsevening
                                args = {'username': user.username, 'role': user.role, 'pe': pe, 'schoolclass': schoolclass, 'notes': booking.notes, 'urltimeslot': timeslot}
                                args['timeslot'] = timeslot[0]+timeslot[1]+":"+timeslot[2]+timeslot[3]
                                args['schoolclasses'] = SchoolClass.objects.filter(Q(students=student) & Q(parentsevening=pe)).values('id', 'subject')

                                # Renders template
                                return render(request, self.template_name, args)
                            else:
                                return redirect('student:class', pe_id, class_id)
                        else:
                            return redirect('student:parentsevening', pe_id)
                    else:
                        return redirect('student:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def time_booked(self, current_timeslot, booked_by_me):

        # Checks if booking exists for this student, class, and parents' evening
        if len(booked_by_me) == 1:

            # Checks if the booking timeslot is the same as the current timeslot
            if booked_by_me[0].timeslot == current_timeslot:
                return True
            else:
                return False
        else:
            return False

class RemoveBookingView(RedirectView):

    def get(self, request, pe_id, class_id, timeslot):
        user = request.user

        # Checks user is logged in
        if user.is_authenticated:

            # Checks user is correct role
            if user.role == "Student":

                # Checks user's account only corresponds to one person
                # Gets the current person
                students = Student.objects.filter(user=user)
                if len(students) == 1:
                    student = students[0]

                    # Checks the current parents' evening exists and it is applicable to this person
                    # Gets the current parents' evening
                    pes = ParentsEvening.objects.filter(Q(id=pe_id) & Q(schoolclasses__students=student)).distinct()
                    if len(pes) == 1:
                        pe = pes[0]

                        # Checks the current class exists, this person is in this class, and the class is applicable to the current parents' evening
                        # Gets the current class
                        schoolclasses = SchoolClass.objects.filter(Q(id=class_id) & Q(students=student) & Q(parentsevening=pe))
                        if len(schoolclasses) == 1:
                            schoolclass = schoolclasses[0]

                            # Converts the timeslot in the url to a 'time' object
                            # Catches error if an invalid timeslot is given in the url
                            try:
                                urltotime = datetime.time(int(timeslot[0]+timeslot[1]), int(timeslot[2]+timeslot[3]), 0)
                            except ValueError:
                                return redirect('student:class', pe_id, class_id)

                            # Checks if the current timeslot is booked by this student for this class in this parents' evening
                            # Gets the booking
                            booked_by_me = PEBooking.objects.filter(Q(parentsevening=pe) & Q(schoolclass=schoolclass) & Q(student=student))
                            if self.time_booked(urltotime, booked_by_me):
                                booking = booked_by_me[0]

                                # Deletes booking record
                                booking.delete()

                                # Redirects back to Class page
                                return redirect('student:class', pe_id, class_id)
                            else:
                                return redirect('student:class', pe_id, class_id)
                        else:
                            return redirect('student:parentsevening', pe_id)
                    else:
                        return redirect('student:welcome')
                else:
                    return redirect('login:logout')
            else:
                return functions.role_redirect(user)
        else:
            return redirect('login:login')

    def time_booked(self, current_timeslot, booked_by_me):

        # Checks if booking exists for this student, class, and parents' evening
        if len(booked_by_me) == 1:

            # Checks if the booking timeslot is the same as the current timeslot
            if booked_by_me[0].timeslot == current_timeslot:
                return True
            else:
                return False
        else:
            return False
