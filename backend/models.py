from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
import os


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


class Profile(models.Model):
    MARITAL_STATUS_CHOICES = [
        ('bekar', 'Bekar'),
        ('bosanmis', 'Boşanmış'),
        ('dul', 'Dul'),
    ]
    
    RELIGIOUS_VIEW_CHOICES = [(i, str(i)) for i in range(6)]  # 0-5 arası
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    eksisozluk_username = models.CharField(max_length=50, unique=True)
    age = models.PositiveIntegerField()
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)
    has_children = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
    religious_view = models.IntegerField(choices=RELIGIOUS_VIEW_CHOICES)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.eksisozluk_username}"


def profile_photo_path(instance, filename):
    """Fotoğrafları profil ID'sine göre klasörle"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(f'profile_photos/{instance.profile.id}', filename)


class ProfilePhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to=profile_photo_path)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'order', 'created_at']
    
    def __str__(self):
        return f"Photo for {self.profile.eksisozluk_username}"
    
    def save(self, *args, **kwargs):
        # Eğer bu fotoğraf primary ise, diğer fotoğrafların primary özelliğini kaldır
        if self.is_primary:
            ProfilePhoto.objects.filter(
                profile=self.profile, 
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class VerificationToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Token for {self.user.email} - {'Used' if self.is_used else 'Valid'}"
    
    def is_valid(self):
        """Token'ın geçerli olup olmadığını kontrol et"""
        if self.is_used:
            return False
        
        # 24 saat geçerlilik süresi
        expiry = self.created_at + timezone.timedelta(hours=24)
        return timezone.now() < expiry