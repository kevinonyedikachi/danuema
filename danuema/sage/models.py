from django.db import models

# Create your models here.
class RefreshToken(models.Model):
    token = models.CharField(max_length = 255)

    def __str__(self):
        return self.token