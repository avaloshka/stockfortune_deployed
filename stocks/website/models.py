from django.db import models


class Charts(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=10)
    img = models.ImageField(upload_to='elements/')

    def __str__(self):
    	return self.name




