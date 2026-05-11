from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import CustomUser, Profile, ProfilePhoto, VerificationToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'profile_link', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    readonly_fields = ('id', 'date_joined', 'last_login')
    
    fieldsets = (
        ('Giriş Bilgileri', {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('username',)}),
        ('Yetkiler', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    def profile_link(self, obj):
        try:
            profile = obj.profile
            url = f"/admin/profiles/profile/{profile.id}/change/"
            return format_html(
                '<a href="{}" style="color: #4CAF50;">📋 Profili Gör</a>',
                url
            )
        except Profile.DoesNotExist:
            return "Profil Yok"  # Düz string, format_html DEĞİL
    
    profile_link.short_description = 'Profil'


class ProfilePhotoInline(admin.TabularInline):
    model = ProfilePhoto
    extra = 0
    max_num = 5
    readonly_fields = ('id', 'created_at', 'photo_preview')
    fields = ('photo_preview', 'photo', 'is_primary', 'order', 'created_at')
    ordering = ('-is_primary', 'order')
    
    def photo_preview(self, obj):
        if obj.photo and hasattr(obj.photo, 'url'):
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; '
                'border-radius: 8px; object-fit: cover;" />',
                obj.photo.url
            )
        return "Fotoğraf yok"  # Düz string
    
    photo_preview.short_description = 'Önizleme'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'eksisozluk_username', 'user_email', 'age', 'city',
        'marital_status_display', 'has_children_display', 
        'religious_view_stars', 'is_public', 'photo_count', 
        'created_at'
    )
    list_filter = ('marital_status', 'has_children', 'is_public', 'city', 'religious_view')
    search_fields = ('eksisozluk_username', 'user__email', 'city')
    readonly_fields = ('id', 'created_at', 'updated_at', 'user_email')
    inlines = [ProfilePhotoInline]
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('id', 'user', 'user_email')
        }),
        ('Profil Bilgileri', {
            'fields': ('eksisozluk_username', 'age', 'marital_status', 
                      'has_children', 'city', 'religious_view')
        }),
        ('Durum ve Tarihler', {
            'fields': ('is_public', 'created_at', 'updated_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def photo_count(self, obj):
        count = obj.photos.count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} 📸</span>',
                count  # PARAMETRE EKLENDİ
            )
        return format_html(
            '<span style="color: red;">{} 📸</span>',
            0  # PARAMETRE EKLENDİ
        )
    photo_count.short_description = 'Fotoğraf'
    
    def religious_view_stars(self, obj):
        stars = '⭐' * obj.religious_view
        empty = '☆' * (5 - obj.religious_view)
        return format_html(
            '<span style="font-size: 1.2em;">{}{}</span> '
            '<span style="color: #666;">({}/5)</span>',
            stars, empty, obj.religious_view  # 3 PARAMETRE
        )
    religious_view_stars.short_description = 'Dini Görüş'
    
    def has_children_display(self, obj):
        if obj.has_children:
            return format_html(
                '<span style="color: #4CAF50;">{}</span>',
                '✓ Var'  # PARAMETRE EKLENDİ
            )
        return format_html(
            '<span style="color: #999;">{}</span>',
            '✗ Yok'  # PARAMETRE EKLENDİ
        )
    has_children_display.short_description = 'Çocuk'
    
    def marital_status_display(self, obj):
        status_map = {
            'bekar': ('#2196F3', '💙 Bekar'),
            'bosanmis': ('#FF9800', '🧡 Boşanmış'),
            'dul': ('#9C27B0', '💜 Dul'),
        }
        color, text = status_map.get(obj.marital_status, ('#666', obj.marital_status))
        return format_html(
            '<span style="color: {};">{}</span>',
            color, text  # 2 PARAMETRE
        )
    marital_status_display.short_description = 'Medeni Durum'
    
    actions = ['make_public', 'make_private']
    
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} profil herkese açık hale getirildi.')
    make_public.short_description = 'Profilleri herkese açık yap'
    
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} profil gizli hale getirildi.')
    make_private.short_description = 'Profilleri gizli yap'


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_link', 'photo_preview', 'is_primary', 'order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('profile__eksisozluk_username', 'profile__user__email')
    readonly_fields = ('id', 'created_at', 'photo_preview')
    
    fieldsets = (
        ('Fotoğraf Bilgileri', {
            'fields': ('id', 'profile', 'photo_preview', 'photo')
        }),
        ('Ayarlar', {
            'fields': ('is_primary', 'order', 'created_at')
        }),
    )
    
    def profile_link(self, obj):
        url = f"/admin/profiles/profile/{obj.profile.id}/change/"
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.profile.eksisozluk_username  # 2 PARAMETRE
        )
    profile_link.short_description = 'Profil'
    profile_link.admin_order_field = 'profile__eksisozluk_username'
    
    def photo_preview(self, obj):
        if obj.photo and hasattr(obj.photo, 'url'):
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 80px; '
                'border-radius: 8px; object-fit: cover;" />',
                obj.photo.url  # PARAMETRE EKLENDİ
            )
        return "Fotoğraf yok"  # Düz string
    
    photo_preview.short_description = 'Önizleme'
    
    actions = ['make_primary', 'remove_primary']
    
    def make_primary(self, request, queryset):
        count = 0
        for photo in queryset:
            ProfilePhoto.objects.filter(profile=photo.profile).update(is_primary=False)
            photo.is_primary = True
            photo.save()
            count += 1
        self.message_user(request, f'{count} fotoğraf ana fotoğraf olarak işaretlendi.')
    make_primary.short_description = '⭐ Ana fotoğraf yap'
    
    def remove_primary(self, request, queryset):
        updated = queryset.update(is_primary=False)
        self.message_user(request, f'{updated} fotoğrafın ana fotoğraf özelliği kaldırıldı.')
    remove_primary.short_description = 'Ana fotoğraf özelliğini kaldır'


@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'token_short', 'is_used', 'is_valid_status', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('id', 'token', 'created_at', 'is_valid_status')
    
    fieldsets = (
        ('Token Bilgileri', {
            'fields': ('id', 'user', 'token', 'created_at')
        }),
        ('Durum', {
            'fields': ('is_used', 'is_valid_status')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Kullanıcı'
    user_email.admin_order_field = 'user__email'
    
    def token_short(self, obj):
        token_str = str(obj.token)
        return f'{token_str[:8]}...{token_str[-4:]}'
    token_short.short_description = 'Token'
    
    def is_valid_status(self, obj):
        if obj.is_valid():
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                '✅ Geçerli'  # PARAMETRE EKLENDİ
            )
        elif obj.is_used:
            return format_html(
                '<span style="color: #999;">{}</span>',
                '✓ Kullanılmış'  # PARAMETRE EKLENDİ
            )
        return format_html(
            '<span style="color: red;">{}</span>',
            '❌ Süresi Dolmuş'  # PARAMETRE EKLENDİ
        )
    is_valid_status.short_description = 'Geçerlilik'
    
    actions = ['mark_as_used', 'mark_as_unused', 'delete_expired_tokens']
    
    def mark_as_used(self, request, queryset):
        updated = queryset.update(is_used=True)
        self.message_user(request, f'{updated} token kullanılmış olarak işaretlendi.')
    mark_as_used.short_description = '✔️ Kullanılmış olarak işaretle'
    
    def mark_as_unused(self, request, queryset):
        updated = queryset.update(is_used=False)
        self.message_user(request, f'{updated} token kullanılmamış olarak işaretlendi.')
    mark_as_unused.short_description = '🔄 Kullanılmamış olarak işaretle'
    
    def delete_expired_tokens(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        expiry_time = timezone.now() - timedelta(hours=24)
        expired = VerificationToken.objects.filter(
            created_at__lt=expiry_time,
            is_used=False
        )
        count = expired.count()
        expired.delete()
        self.message_user(request, f'{count} süresi dolmuş token silindi.')
    delete_expired_tokens.short_description = '🗑️ Süresi dolmuş tokenları sil'


# Admin panel özelleştirmeleri
admin.site.site_header = '🍋 EkşiMatch Admin Paneli'
admin.site.site_title = 'EkşiMatch Yönetim'
admin.site.index_title = 'Yönetim Paneli'