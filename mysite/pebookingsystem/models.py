from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager

##### Accounts #####

class User(AbstractBaseUser):

    # Create the fields (password field inherited from AbstractBaseUser)
    username = models.CharField(max_length=30, unique=True)
    role = models.CharField(max_length=30)
    pin = models.IntegerField(null=True)

    # Let Django know what to use as the username
    USERNAME_FIELD = 'username'

    # Let Django know to use the ModelManager for Users
    objects = UserManager()

    def __str__(self):
        return self.username

class Student(models.Model):

    # Create the fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=256)
    schoolyear = models.IntegerField()

    def __str__(self):
        return self.fullname

class Parent(models.Model):

    # Create the fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=256)
    children = models.ManyToManyField(Student)

    def __str__(self):
        return self.fullname

class Teacher(models.Model):

    # Create the fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=256)
    title = models.CharField(max_length=10)
    subject = models.CharField(max_length=256)

    def __str__(self):
        return self.fullname

class Admin(models.Model):

    # Create the fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=256)

    def __str__(self):
        return self.fullname

##### Other #####

class SchoolClass(models.Model):

    # Create the fields
    classname = models.CharField(max_length=256)
    subject = models.CharField(max_length=256)
    schoolyear = models.IntegerField()
    students = models.ManyToManyField(Student)
    teachers = models.ManyToManyField(Teacher)
    details = models.TextField()

    def __str__(self):
        return self.classname

class ParentsEvening(models.Model):

    # Create the fields
    pename = models.CharField(max_length=256)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    appointmentlength = models.TimeField()
    schoolclasses = models.ManyToManyField(SchoolClass)
    details = models.TextField()

    def __str__(self):
        return self.pename

class PEBooking(models.Model):

    # Create the fields
    parentsevening = models.ForeignKey(ParentsEvening, on_delete=models.CASCADE)
    schoolclass = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timeslot = models.TimeField()
    notes = models.TextField()
