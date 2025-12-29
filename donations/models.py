from django.db import models
from django.conf import settings

# Create your models here.
class donationData(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    contributionType=models.CharField(max_length=20)
    imageName = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True)
    message = models.TextField(blank=True)
    addres = models.TextField(default="")
    city = models.CharField(max_length=100,default="")
    pincode = models.CharField(max_length=10,default=000000)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        default="pending"
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    company_name = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"{self.name} - {self.contributionType}"