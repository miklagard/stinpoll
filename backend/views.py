from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from rest_framework.authtoken.models import Token
from .models import Profile, ProfilePhoto, VerificationToken
from .serializers import (
    UserRegistrationSerializer, 
    ProfileSerializer, 
    ProfileUpdateSerializer,
    ProfilePhotoSerializer
)
import logging
from django.middleware.csrf import get_token
from django.http import JsonResponse


logger = logging.getLogger(__name__)
User = get_user_model()


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Profil CRUD işlemleri için ViewSet
    """
    queryset = Profile.objects.all()
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Action'a göre serializer seç"""
        if self.action in ['update', 'partial_update']:
            return ProfileUpdateSerializer
        return ProfileSerializer
    
    def get_queryset(self):
        """Kullanıcı sadece kendi profilini görebilir"""
        if self.request.user.is_authenticated:
            return Profile.objects.filter(user=self.request.user)
        return Profile.objects.none()
    
    def perform_create(self, serializer):
        """Profil oluştururken kullanıcıyı otomatik ata"""
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Kullanıcının zaten profili varsa hata döndür"""
        if Profile.objects.filter(user=request.user).exists():
            return Response(
                {'error': 'Zaten bir profiliniz var.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def set_primary_photo(self, request, pk=None):
        """Ana fotoğrafı değiştir"""
        profile = self.get_object()
        photo_id = request.data.get('photo_id')
        
        try:
            # Tüm fotoğrafların primary özelliğini kaldır
            profile.photos.update(is_primary=False)
            # Seçili fotoğrafı primary yap
            photo = profile.photos.get(id=photo_id)
            photo.is_primary = True
            photo.save()
            
            return Response(
                {'message': 'Ana fotoğraf güncellendi.'},
                status=status.HTTP_200_OK
            )
        except ProfilePhoto.DoesNotExist:
            return Response(
                {'error': 'Fotoğraf bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def delete_photo(self, request, pk=None):
        """Belirli bir fotoğrafı sil"""
        profile = self.get_object()
        photo_id = request.data.get('photo_id')
        
        try:
            photo = profile.photos.get(id=photo_id)
            
            # Ana fotoğraf siliniyorsa, başka bir fotoğrafı ana yap
            was_primary = photo.is_primary
            photo.delete()
            
            if was_primary:
                first_photo = profile.photos.first()
                if first_photo:
                    first_photo.is_primary = True
                    first_photo.save()
            
            return Response(
                {'message': 'Fotoğraf silindi.'},
                status=status.HTTP_200_OK
            )
        except ProfilePhoto.DoesNotExist:
            return Response(
                {'error': 'Fotoğraf bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Kullanıcı kaydı
    - Email ve şifre ile kayıt
    - Doğrulama emaili gönderir
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Verification token oluştur
        token = VerificationToken.objects.create(user=user)
        
        # Email içeriği
        verification_url = f"http://localhost:5173/verify/{token.token}"
        delete_url = f"http://localhost:8000/api/delete-account/{token.token}"
        
        # Email gönder
        try:
            send_mail(
                'Hesap Doğrulama - Çöpçatan',
                f'''Merhaba,
                
Hesabınızı doğrulamak için aşağıdaki linke tıklayın:
{verification_url}

Hesabınızı silmek için:
{delete_url}

Bu emaili yanlışlıkla aldıysanız lütfen dikkate almayın.
''',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Email gönderme hatası: {e}")
            # Email gönderilemezse kullanıcıyı silme, sadece logla
        
        return Response(
            {
                'message': 'Doğrulama emaili gönderildi. Lütfen emailinizi kontrol edin.',
                'user_id': user.id
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email(request, token):
    """
    Email doğrulama
    - Token'ı kontrol eder
    - Kullanıcıyı aktif eder
    """
    try:
        verification = VerificationToken.objects.get(token=token)
    except VerificationToken.DoesNotExist:
        return Response(
            {'error': 'Geçersiz doğrulama linki.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Token zaten kullanılmış mı?
    if verification.is_used:
        return Response(
            {'error': 'Bu doğrulama linki zaten kullanılmış.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Token süresi dolmuş mu? (24 saat)
    token_age = timezone.now() - verification.created_at
    if token_age.days >= 1:
        return Response(
            {'error': 'Doğrulama linkinin süresi dolmuş. Lütfen tekrar kayıt olun.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Kullanıcıyı aktif et (token'ı henüz kullanılmış işaretleme)
    user = verification.user
    user.is_active = True
    user.save()
    
    return Response(
        {
            'message': 'Email başarıyla doğrulandı. Şimdi şifrenizi belirleyebilirsiniz.',
            'token': str(verification.token),
            'email': user.email
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def set_password_and_login(request, token):
    """
    Şifre belirleme ve otomatik login
    - Şifreyi ayarlar
    - Auth token döndürür (otomatik login)
    - Verification token'ı kullanılmış olarak işaretler
    """
    try:
        verification = VerificationToken.objects.get(token=token)
    except VerificationToken.DoesNotExist:
        return Response(
            {'error': 'Geçersiz token.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Token kontrolü
    if verification.is_used:
        return Response(
            {'error': 'Bu token zaten kullanılmış.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    token_age = timezone.now() - verification.created_at
    if token_age.days >= 1:
        return Response(
            {'error': 'Token süresi dolmuş. Lütfen tekrar kayıt olun.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = verification.user
    
    # Kullanıcıyı aktif et (eğer değilse)
    if not user.is_active:
        user.is_active = True
    
    # Şifre validasyonu
    password = request.data.get('password')
    if not password:
        return Response(
            {'error': 'Şifre gerekli.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(password) < 6:
        return Response(
            {'error': 'Şifre en az 6 karakter olmalıdır.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Şifreyi ayarla
    user.set_password(password)
    user.save()
    
    # Token'ı kullanılmış olarak işaretle
    verification.is_used = True
    verification.save()
    
    # Otomatik login için auth token oluştur
    auth_token, created = Token.objects.get_or_create(user=user)
    
    logger.info(f"Kullanıcı kaydı tamamlandı: {user.email}")
    
    return Response(
        {
            'message': 'Hesabınız başarıyla oluşturuldu.',
            'token': auth_token.key,
            'user_id': user.id,
            'email': user.email
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """
    Kullanıcı girişi
    - Email ve şifre ile giriş
    - Auth token döndürür
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Validasyon
    if not email or not password:
        return Response(
            {'error': 'Email ve şifre gerekli.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Email ile kullanıcıyı bul
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Geçersiz email veya şifre.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Kullanıcı aktif mi?
    if not user.is_active:
        return Response(
            {'error': 'Hesabınız henüz doğrulanmamış. Lütfen emailinizi kontrol edin.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Şifre doğrulama
    user = authenticate(username=user.username, password=password)
    
    if not user:
        return Response(
            {'error': 'Geçersiz email veya şifre.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Token oluştur veya mevcut token'ı al
    token, created = Token.objects.get_or_create(user=user)
    
    logger.info(f"Kullanıcı giriş yaptı: {user.email}")
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'email': user.email
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Kullanıcı çıkışı
    - Auth token'ı siler
    """
    try:
        request.user.auth_token.delete()
        return Response(
            {'message': 'Başarıyla çıkış yapıldı.'},
            status=status.HTTP_200_OK
        )
    except Exception:
        return Response(
            {'error': 'Çıkış yapılırken bir hata oluştu.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def delete_account(request, token):
    """
    Hesap silme (email'deki link ile)
    - Token doğrulaması yapar
    - Kullanıcıyı ve ilişkili tüm verileri siler
    """
    try:
        verification = VerificationToken.objects.get(token=token)
        user = verification.user
        
        # Kullanıcıyı sil (CASCADE ile profil ve fotoğraflar da silinir)
        user_email = user.email
        user.delete()
        
        logger.info(f"Hesap silindi: {user_email}")
        
        return Response(
            {'message': 'Hesabınız başarıyla silindi.'},
            status=status.HTTP_200_OK
        )
    except VerificationToken.DoesNotExist:
        return Response(
            {'error': 'Geçersiz silme linki.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Giriş yapmış kullanıcının profilini getir
    """
    try:
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response(
            {'error': 'Profil bulunamadı.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_csrf_token(request):
    """CSRF token'ı döndür"""
    return JsonResponse({'csrfToken': get_token(request)})