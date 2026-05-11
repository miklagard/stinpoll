from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, ProfilePhoto, VerificationToken

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Kullanıcı kaydı için serializer
    """
    password = serializers.CharField(
        write_only=True, 
        min_length=6,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('email', 'password', 'username')
        extra_kwargs = {
            'username': {'required': False}
        }
    
    def validate_email(self, value):
        """Email benzersiz olmalı"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email adresi zaten kayıtlı.")
        return value
    
    def create(self, validated_data):
        """Kullanıcı oluştur"""
        email = validated_data['email']
        password = validated_data['password']
        username = validated_data.get('username', email)
        
        user = User.objects.create_user(
            email=email,
            password=password,
            username=username
        )
        return user


class ProfilePhotoSerializer(serializers.ModelSerializer):
    """
    Profil fotoğrafı serializer'ı
    """
    class Meta:
        model = ProfilePhoto
        fields = ['id', 'photo', 'is_primary', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProfileSerializer(serializers.ModelSerializer):
    """
    Profil serializer'ı (oluşturma ve görüntüleme için)
    """
    email = serializers.EmailField(source='user.email', read_only=True)
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    photos = ProfilePhotoSerializer(many=True, read_only=True)
    uploaded_photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user_id', 'email', 'eksisozluk_username',
            'photos', 'uploaded_photos', 'age', 'marital_status',
            'has_children', 'city', 'religious_view', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_id', 'email', 'is_public',
            'created_at', 'updated_at'
        ]
    
    def validate_age(self, value):
        """Yaş validasyonu"""
        if value < 18:
            raise serializers.ValidationError("Yaş en az 18 olmalıdır.")
        if value > 120:
            raise serializers.ValidationError("Geçerli bir yaş giriniz.")
        return value
    
    def validate_religious_view(self, value):
        """Dini görüş validasyonu (0-5 arası)"""
        if value < 0 or value > 5:
            raise serializers.ValidationError("Dini görüş 0-5 arası olmalıdır.")
        return value
    
    def validate_uploaded_photos(self, value):
        """Fotoğraf sayısı kontrolü"""
        if len(value) > 5:
            raise serializers.ValidationError("En fazla 5 fotoğraf yükleyebilirsiniz.")
        return value
    
    def validate_eksisozluk_username(self, value):
        """Ekşisözlük kullanıcı adı benzersiz olmalı"""
        if Profile.objects.filter(eksisozluk_username=value).exists():
            raise serializers.ValidationError("Bu ekşisözlük kullanıcı adı zaten kullanılıyor.")
        return value
    
    def create(self, validated_data):
        """Profil ve fotoğrafları oluştur"""
        uploaded_photos = validated_data.pop('uploaded_photos', [])
        profile = Profile.objects.create(**validated_data)
        
        # Fotoğrafları kaydet
        for i, photo in enumerate(uploaded_photos):
            ProfilePhoto.objects.create(
                profile=profile,
                photo=photo,
                is_primary=(i == 0),  # İlk fotoğraf primary olsun
                order=i
            )
        
        return profile


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Profil güncelleme serializer'ı
    """
    new_photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    delete_photo_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Profile
        fields = [
            'eksisozluk_username', 'age', 'marital_status',
            'has_children', 'city', 'religious_view',
            'new_photos', 'delete_photo_ids'
        ]
    
    def validate_age(self, value):
        """Yaş validasyonu"""
        if value < 18:
            raise serializers.ValidationError("Yaş en az 18 olmalıdır.")
        if value > 120:
            raise serializers.ValidationError("Geçerli bir yaş giriniz.")
        return value
    
    def validate_religious_view(self, value):
        """Dini görüş validasyonu"""
        if value < 0 or value > 5:
            raise serializers.ValidationError("Dini görüş 0-5 arası olmalıdır.")
        return value
    
    def validate_eksisozluk_username(self, value):
        """Ekşisözlük kullanıcı adı benzersiz olmalı (kendi profili hariç)"""
        if self.instance and Profile.objects.filter(
            eksisozluk_username=value
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Bu ekşisözlük kullanıcı adı zaten kullanılıyor.")
        return value
    
    def validate_new_photos(self, value):
        """Yeni fotoğraf sayısı kontrolü"""
        if self.instance:
            current_count = self.instance.photos.count()
            delete_count = len(self.initial_data.get('delete_photo_ids', []))
            new_count = len(value)
            
            total_after_update = current_count - delete_count + new_count
            
            if total_after_update > 5:
                raise serializers.ValidationError(
                    f"En fazla 5 fotoğrafınız olabilir. "
                    f"Mevcut: {current_count}, Silinecek: {delete_count}, "
                    f"Eklenecek: {new_count}"
                )
        return value
    
    def update(self, instance, validated_data):
        """Profil güncelleme"""
        new_photos = validated_data.pop('new_photos', [])
        delete_photo_ids = validated_data.pop('delete_photo_ids', [])
        
        # Profil bilgilerini güncelle
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Silinecek fotoğrafları sil
        if delete_photo_ids:
            deleted_photos = ProfilePhoto.objects.filter(
                profile=instance,
                id__in=delete_photo_ids
            )
            
            # Silinen fotoğraflar arasında primary var mı kontrol et
            had_primary = deleted_photos.filter(is_primary=True).exists()
            deleted_photos.delete()
            
            # Eğer primary fotoğraf silindiyse, yeni primary ata
            if had_primary:
                first_remaining = instance.photos.first()
                if first_remaining:
                    first_remaining.is_primary = True
                    first_remaining.save()
        
        # Yeni fotoğrafları ekle
        current_count = instance.photos.count()
        for i, photo in enumerate(new_photos):
            ProfilePhoto.objects.create(
                profile=instance,
                photo=photo,
                is_primary=(current_count == 0 and i == 0),  # Hiç fotoğraf yoksa ilk eklenen primary olsun
                order=current_count + i
            )
        
        return instance


class VerificationTokenSerializer(serializers.ModelSerializer):
    """
    Doğrulama token'ı serializer'ı (admin için)
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = VerificationToken
        fields = ['id', 'user', 'user_email', 'token', 'created_at', 'is_used', 'is_valid']
        read_only_fields = ['id', 'token', 'created_at']
    
    def get_is_valid(self, obj):
        """Token geçerlilik durumu"""
        return obj.is_valid()


class UserLoginSerializer(serializers.Serializer):
    """
    Kullanıcı girişi için serializer
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )


class PasswordSetSerializer(serializers.Serializer):
    """
    Şifre belirleme için serializer
    """
    password = serializers.CharField(
        min_length=6,
        style={'input_type': 'password'},
        write_only=True
    )
    password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=False
    )
    
    def validate(self, data):
        """Şifreler eşleşmeli"""
        if 'password_confirm' in data and data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Şifreler eşleşmiyor.'
            })
        return data


class DeleteAccountSerializer(serializers.Serializer):
    """
    Hesap silme onayı için serializer
    """
    confirmation = serializers.BooleanField(required=True)
    
    def validate_confirmation(self, value):
        if not value:
            raise serializers.ValidationError("Hesap silme işlemini onaylamalısınız.")
        return value