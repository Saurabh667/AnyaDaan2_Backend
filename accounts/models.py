from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    company_name = models.CharField(max_length=255,blank=True,null=True)
    role = models.CharField(max_length=100,blank=True,null=True)
    phone = models.CharField(max_length=15,blank=True,null=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


    def __str__(self):
        return self.email
