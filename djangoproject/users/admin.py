from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.conf import settings

CustomUser = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'role', 'user_actions')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'role')
    ordering = ('username',)
    readonly_fields = ('user_actions',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'role', 'user_actions')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'role')
        }),
    )
    
    def user_actions(self, obj):
        if not obj.pk:
            return "Guardar el usuario primero"
            
        # Botón para bloquear/desbloquear
        action = "desbloquear" if not obj.is_active else "bloquear"
        toggle_url = reverse('admin:toggle_user_active', args=[obj.pk])
        toggle_btn = format_html(
            '<a class="button" href="{}" style="margin-bottom: 8px; display: inline-block;">{}</a>',
            toggle_url,
            f'{action.capitalize()} usuario'
        )
        
        # Botón para cambiar contraseña (usa tu URL existente)
        change_pwd_url = reverse('users:change_password') + f'?user_id={obj.pk}'
        change_pwd_btn = format_html(
            '<a class="button change-pwd" href="{}" style="background: #5b80b2; margin-bottom: 8px; display: inline-block;">Cambiar contraseña</a>',
            change_pwd_url
        )
        
        # Estado actual
        status = format_html(
            '<div style="margin-top:8px"><small>Estado: <strong>{}</strong></small></div>',
            "Activo" if obj.is_active else "Inactivo"
        )
        
        return format_html(
            '{}<br>{}<br>{}',
            toggle_btn,
            change_pwd_btn,
            status
        )
    
    user_actions.short_description = 'Acciones rápidas'
    user_actions.allow_tags = True
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/toggle_active/',
                self.admin_site.admin_view(self.toggle_user_active),
                name='toggle_user_active',
            ),
        ]
        return custom_urls + urls
    
    def toggle_user_active(self, request, user_id):
        user = CustomUser.objects.get(pk=user_id)
        user.is_active = not user.is_active
        user.save()
        self.message_user(request, f'Usuario {user.username} ha sido {"desbloqueado" if user.is_active else "bloqueado"}')
        
        # Redirige a la página desde donde vino la solicitud
        if 'HTTP_REFERER' in request.META:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        return HttpResponseRedirect(reverse('admin:accounts_customuser_changelist'))
    
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }