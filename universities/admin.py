from django.contrib import admin
from .models import University, Faculty, MyUniversity, Review


class FacultyInline(admin.TabularInline):
    model = Faculty
    extra = 1


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'city', 'degree_level', 'tuition_fee', 'duration', 'dormitory_available', 'ielts_required', 'sat_required', 'save_count', 'created_at']
    list_filter = ['country', 'degree_level', 'dormitory_available', 'ielts_required', 'sat_required']
    search_fields = ['name', 'city', 'country']
    inlines = [FacultyInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'country', 'city', 'tuition_fee', 'duration', 'degree_level', 'description', 'logo')
        }),
        ('Accommodation', {
            'fields': ('dormitory_available',)
        }),
        ('Scholarships', {
            'fields': ('scholarships',),
            'description': 'Enter scholarships separated by commas.'
        }),
        ('Admission Requirements', {
            'fields': ('ielts_required', 'ielts_score', 'sat_required', 'sat_score')
        }),
    )

    def save_count(self, obj):
        return obj.saved_by.count()
    save_count.short_description = 'Saves'


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['name', 'university', 'degree_level', 'subject_group', 'last_year_score']
    list_filter = ['degree_level', 'university', 'subject_group', 'language']
    search_fields = ['name', 'university__name']


@admin.register(MyUniversity)
class MyUniversityAdmin(admin.ModelAdmin):
    list_display = ['user', 'university', 'added_at']
    list_filter = ['university']
    search_fields = ['user__username', 'university__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'university', 'rating', 'recommend', 'is_verified', 'created_at']
    list_filter = ['rating', 'recommend', 'is_verified', 'university']
    search_fields = ['user__username', 'university__name', 'title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_verified']
    fieldsets = (
        ('Review Info', {
            'fields': ('university', 'user', 'rating', 'title', 'recommend', 'is_verified')
        }),
        ('Content', {
            'fields': ('experience', 'pros', 'cons', 'tips')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
