import random
import datetime

from django.shortcuts import redirect
from django.db.models import Q

from .models import *

# Redirects to correct Welcome page or to Logout if user does not have valid role
def role_redirect(user):
    if user.role == "Admin":
        return redirect('admin:welcome')
    elif user.role == "Teacher":
        return redirect('teacher:welcome')
    elif user.role == "Parent":
        return redirect('parent:welcome')
    elif user.role == "Student":
        return redirect('student:welcome')
    else:
        return redirect('login:logout')

# Returns Student, Parent, Teacher, Admin, or 'None' depending on the role of the user
def get_person(user):
    if user.role == "Admin":
        people = Admin.objects.filter(user=user)
    elif user.role == "Teacher":
        people = Teacher.objects.filter(user=user)
    elif user.role == "Parent":
        people = Parent.objects.filter(user=user)
    elif user.role == "Student":
        people = Student.objects.filter(user=user)
    else:
        people = []

    if len(people) == 1:
        return people[0]
    else:
        return None

# Gets all the conflicts of a class' teachers
def get_teacher_conflicts(pe, schoolclass):
    conflicts = []

    # Get number of teachers for this class
    # Get bookings for teachers teaching this class for this parents' evening
    teachers_count = Teacher.objects.filter(schoolclass=schoolclass).count()
    all_bookings = PEBooking.objects.filter(Q(schoolclass__teachers__schoolclass=schoolclass) & Q(parentsevening=pe))


    # Create lists for unique bookings and any duplicates
    teacher_bookings = []
    teacher_double_bookings = []

    # Populate lists from before
    for booking in all_bookings:
        if booking not in teacher_bookings:
            teacher_bookings.append(booking)
        else:
            teacher_double_bookings.append(booking)

    # Counts number of duplicates
    # Add booking's timeslot to conflicts if number of duplicates is equal to number of teachers for this class
    # Converts timeslot to 'timedelta' so calculations can be performed
    for booking in teacher_bookings:
        count = 1
        for double_booking in teacher_double_bookings:
            if booking == double_booking:
                count += 1
        if count == teachers_count:
            conflicts.append(datetime.timedelta(hours=booking.timeslot.hour, minutes=booking.timeslot.minute, seconds=0))

    return conflicts

# Generates a free PIN
def generate_pin():
    # Generates random number
    pin = random.randint(1000, 9999)

    # Counts number of tries until all PINs have been tried
    tries = 0
    while tries < 9000:

        # Checks if PIN is free, if so, return PIN
        # If not, increment by 1 and try again
        conflicts = User.objects.filter(pin=pin)
        if len(conflicts) == 0:
            return pin
        else:
            tries += 1
            if pin < 9999:
                pin += 1
            else:
                pin = 1000

    return 0
