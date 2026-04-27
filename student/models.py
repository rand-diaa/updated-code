from django.db import models
from django.contrib.auth.models import User

ACADEMIC_YEAR_CHOICES = (
    (1, 'Year 1'),
    (2, 'Year 2'),
    (3, 'Year 3'),
    (4, 'Year 4'),
)


class Student(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    profile_pic= models.ImageField(upload_to='profile_pic/Student/',null=True,blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    mobile = models.CharField(max_length=20,null=False)
    academic_year = models.PositiveSmallIntegerField(choices=ACADEMIC_YEAR_CHOICES, default=1)
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name