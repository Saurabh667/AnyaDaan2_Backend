from django.db import models

# Create your models here.
class donationData(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    contributionType=models.CharField(max_length=20)
    imageName = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True)
    message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} - {self.contributionType}"