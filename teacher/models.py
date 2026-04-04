from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/Teacher/',null=True,blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    mobile = models.CharField(max_length=20,null=False)
    # Phase 1: Auto-approve teachers (status=True by default)
    status= models.BooleanField(default=True)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name