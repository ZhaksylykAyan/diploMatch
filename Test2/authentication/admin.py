from django.contrib import admin
from .models import CustomUser, OTPCode

# Customizing the User Admin
@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_staff', 'is_active', 'date_joined', 'role')
    list_filter = ('is_staff', 'is_active', 'role')
    search_fields = ('email', 'role')
    ordering = ('date_joined',)

# Customizing the OTPCode Admin
@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__email', 'code')
    ordering = ('-created_at',)
    readonly_fields = ('code', 'created_at')