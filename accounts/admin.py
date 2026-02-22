from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'father_name', 'role', 'study_location', 'created_at']
    list_filter = ['role', 'study_location']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
