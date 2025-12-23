from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    company_name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
