from django.db import models
from django.contrib.auth.models import User


class University(models.Model):
    DEGREE_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('both', 'Bachelor & Master'),
    ]

    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)
    degree_level = models.CharField(max_length=20, choices=DEGREE_CHOICES, default='both')
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='university_logos/', blank=True, null=True)

    # Accommodation
    dormitory_available = models.BooleanField(default=False)

    # Scholarships (comma-separated list)
    scholarships = models.TextField(
        blank=True,
        help_text='Enter scholarships separated by commas e.g. "Merit Scholarship, Need-Based Grant"'
    )

    # Admission requirements
    ielts_required = models.BooleanField(default=False)
    ielts_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True,
                                      help_text='Minimum IELTS score e.g. 6.5')
    sat_required = models.BooleanField(default=False)
    sat_score = models.IntegerField(null=True, blank=True,
                                    help_text='Minimum SAT score e.g. 1200')

    # QS World Ranking
    qs_ranking = models.IntegerField(null=True, blank=True,
                                     help_text='QS World University Ranking number (lower is better)')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Universities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.country})"

    def save_count(self):
        return self.saved_by.count()

    def scholarship_list(self):
        if not self.scholarships:
            return []
        return [s.strip() for s in self.scholarships.split(',') if s.strip()]


class Faculty(models.Model):
    DEGREE_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('both', 'Bachelor & Master'),
    ]

    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='faculties')
    name = models.CharField(max_length=200)
    degree_level = models.CharField(max_length=20, choices=DEGREE_CHOICES, default='bachelor')
    description = models.TextField(blank=True)

    # Payment info — mirrors real DİM/TQDK data
    state_order_places = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Number of state-funded (grant) places available (0 = none)'
    )
    tuition_paid = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Annual tuition for fee-paying students (AZN or USD)'
    )

    class Meta:
        verbose_name_plural = 'Faculties'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.university.name}"

    def payment_display(self):
        """Human-readable payment label for the rank card."""
        parts = []
        if self.state_order_places:
            parts.append(f'Dövlət sifarişi ({self.state_order_places} yer)')
        if self.tuition_paid:
            parts.append(f'Ödənişli ({self.tuition_paid} AZN)')
        return ' / '.join(parts) if parts else 'Məlumat yoxdur'


class MyUniversity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_universities')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='saved_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'university')
        verbose_name_plural = 'My Universities'
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} → {self.university.name}"


class Review(models.Model):
    RATING_CHOICES = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]
    RECOMMEND_CHOICES = [('yes', 'Yes'), ('no', 'No')]

    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')

    # Core fields
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=150)
    experience = models.TextField(help_text='Describe your overall experience')
    pros = models.TextField(help_text='List the key advantages')
    cons = models.TextField(help_text='List the key disadvantages')
    tips = models.TextField(help_text='Advice for future applicants', blank=True)
    recommend = models.CharField(max_length=3, choices=RECOMMEND_CHOICES)

    # Trust / moderation
    is_verified = models.BooleanField(
        default=False,
        help_text='Mark as Verified Participant if the user\'s participation is confirmed'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # One review per user per university
        unique_together = ('university', 'user')
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f'{self.user.username} → {self.university.name} ({self.rating}★)'


class RankEntry(models.Model):
    """Stores a user's personal faculty ranking list (ordered)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rank_entries')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='rank_entries')
    position = models.PositiveSmallIntegerField(help_text='1 = top choice')
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        unique_together = ('user', 'faculty')
        verbose_name_plural = 'Rank Entries'

    def __str__(self):
        return f'{self.user.username} #{self.position} → {self.faculty.name} ({self.faculty.university.name})'
