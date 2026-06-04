# yourapp/management/commands/resend_activation_email.py

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from backend.models import VerificationToken  # models.py'nizin bulunduğu yere göre değiştirin
from dotenv import dotenv_values
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Belirtilen kullanıcıya hesap etkinleştirme emailini yeniden gönderir'

    def add_arguments(self, parser):
        # İlk parametre (zorunlu) - ana email adresi
        parser.add_argument(
            'email',
            type=str,
            help='Aktivasyon emailinin gönderileceği ana email adresi'
        )
        
        # İkinci parametre (opsiyonel) - alternatif email adresi
        parser.add_argument(
            '--alt-email',
            type=str,
            dest='alt_email',
            help='Alternatif email adresi (bu adrese gönderilir, ana email adresi yerine)'
        )

    def handle(self, *args, **options):
        email = options['email']
        alt_email = options.get('alt_email')
        
        # Gönderilecek email adresini belirle
        target_email = alt_email if alt_email else email
        
        # Kullanıcıyı bul
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f'"{email}" email adresine sahip kullanıcı bulunamadı.')
        
        # Kullanıcı zaten aktif mi kontrol et
        if user.is_active:
            self.stdout.write(
                self.style.WARNING(f'Kullanıcı "{email}" zaten aktif durumda.')
            )
            return
        
        # Mevcut verification token'ı kontrol et
        try:
            verification = VerificationToken.objects.get(user=user, is_used=False)
            
            # Token süresi dolmuş mu kontrol et
            token_age = timezone.now() - verification.created_at
            if token_age.days >= 1:
                # Süresi dolmuş token'ı sil ve yeni oluştur
                verification.delete()
                verification = VerificationToken.objects.create(user=user)
                self.stdout.write(self.style.NOTICE('Token süresi dolmuştu, yeni token oluşturuldu.'))
            else:
                self.stdout.write(self.style.NOTICE('Mevcut geçerli token kullanılıyor.'))
                
        except VerificationToken.DoesNotExist:
            # Yeni token oluştur
            verification = VerificationToken.objects.create(user=user)
            self.stdout.write(self.style.NOTICE('Yeni token oluşturuldu.'))
        
        # .env dosyasından domain bilgisini al
        config = dotenv_values(settings.BASE_DIR / '.env')
        domain = config.get('DOMAIN', 'http://localhost:8000')
        
        # Email içeriği
        verification_url = f"{domain}/verify/{verification.token}"
        delete_url = f"{domain}/delete-account/{verification.token}"
        
        # Email gönder
        try:
            send_mail(
                'Hesap Doğrulama - Stinpoll',
                f'''Merhaba {user.username if user.username else user.email},

Hesabınızı doğrulamak için aşağıdaki linke tıklayın:
{verification_url}

Hesabınızı silmek için:
{delete_url}

Bu emaili yanlışlıkla aldıysanız lütfen dikkate almayın.

Not: Bu email "{email}" adresine kayıtlı hesap için talep üzerine gönderilmiştir.
''',
                settings.EMAIL_HOST_USER,
                [target_email],
                fail_silently=False,
            )
            
            # Başarı mesajı
            if alt_email:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Aktivasyon emaili "{alt_email}" adresine gönderildi '
                        f'(orijinal kullanıcı: {email})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Aktivasyon emaili "{email}" adresine yeniden gönderildi.'
                    )
                )
                
            # Loglama
            logger.info(f"Resend activation email to {target_email} (original user: {email})")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Email gönderilemedi: {str(e)}')
            )
            logger.error(f"Email gönderme hatası: {e}")
            raise CommandError(f'Email gönderilemedi: {str(e)}')