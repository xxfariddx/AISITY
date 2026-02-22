from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('applicant', 'Applicant (Abituriyent)'),
        ('student', 'Student'),
    ]
    STUDY_LOCATION_CHOICES = [
        ('azerbaijan', 'Azerbaijan'),
        ('abroad', 'Abroad'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    father_name = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    study_location = models.CharField(max_length=20, choices=STUDY_LOCATION_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Academic scores
    ielts_score = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(9.0)],
        help_text='IELTS score between 0.0 and 9.0'
    )
    sat_score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(400), MaxValueValidator(1600)],
        help_text='SAT score between 400 and 1600'
    )
    dim_score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(700)],
        help_text='DİM score between 0 and 700'
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def is_profile_complete(self):
        return bool(self.role and self.study_location)
