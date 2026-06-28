from django.db import models
from accounts.models import AuthUser
# Create your models here.

class City(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,db_index=True)
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9,decimal_places=6,db_index=True)
    longitude = models.DecimalField(max_digits=9,decimal_places=6,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['latitude']),
            models.Index(fields=['longitude'])
        ]

    def __str__(self):

        return f'{self.name}'
    
class UserCity(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AuthUser,on_delete=models.CASCADE,related_name='user_cities')
    city = models.ForeignKey(City,on_delete=models.CASCADE,related_name='city_users')
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    
    class Meta:
        unique_together = ('user','city')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at'])
        ]

    def __str__(self):
        return f'{self.user.username},{self.city.name}'