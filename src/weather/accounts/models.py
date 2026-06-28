from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
import uuid

class AuthUserManager(BaseUserManager):

    def create_user(self,username,email,password=None,**extra_field):
        if not username:
            raise ValueError('Username is required')
        if not email:
            raise ValueError('Email is required')
        
        user = self.model(username=username,email=email,**extra_field)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
class AuthUser(AbstractUser):

    id = models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True)
    # name = models.CharField(max_length=255,blank=True,null=True)
    address = models.TextField(blank=True,null=True)
    createddt = models.DateTimeField(auto_now_add=True)

    objects = AuthUserManager()

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.username