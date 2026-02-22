from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'star-radio'}),
        label='Your Rating'
    )
    recommend = forms.ChoiceField(
        choices=Review.RECOMMEND_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'recommend-radio'}),
        label='Would you recommend this university?'
    )
    title = forms.CharField(
        max_length=150,
        label='Review Title',
        widget=forms.TextInput(attrs={'placeholder': 'Summarise your experience in one sentence'})
    )
    experience = forms.CharField(
        label='Your Experience',
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Describe your overall experience at this university...'
        })
    )
    pros = forms.CharField(
        label='Pros',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'What did you like most? (one per line)'
        })
    )
    cons = forms.CharField(
        label='Cons',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'What could be improved? (one per line)'
        })
    )
    tips = forms.CharField(
        required=False,
        label='Tips for Future Applicants',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Any advice you wish you had known before applying? (optional)'
        })
    )

    class Meta:
        model = Review
        fields = ['rating', 'title', 'experience', 'pros', 'cons', 'tips', 'recommend']

    def clean_rating(self):
        value = self.cleaned_data.get('rating')
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise forms.ValidationError('Please select a rating.')
        if value < 1 or value > 5:
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return value

    def clean_recommend(self):
        value = self.cleaned_data.get('recommend')
        if value not in ('yes', 'no'):
            raise forms.ValidationError('Please select Yes or No.')
        return value

    def clean_title(self):
        value = self.cleaned_data.get('title', '').strip()
        if not value:
            raise forms.ValidationError('Please provide a review title.')
        if len(value) < 5:
            raise forms.ValidationError('Title must be at least 5 characters.')
        return value

    def clean_experience(self):
        value = self.cleaned_data.get('experience', '').strip()
        if not value:
            raise forms.ValidationError('Please describe your experience.')
        if len(value) < 20:
            raise forms.ValidationError('Experience description must be at least 20 characters.')
        return value

    def clean_pros(self):
        value = self.cleaned_data.get('pros', '').strip()
        if not value:
            raise forms.ValidationError('Please list at least one pro.')
        return value

    def clean_cons(self):
        value = self.cleaned_data.get('cons', '').strip()
        if not value:
            raise forms.ValidationError('Please list at least one con.')
        return value
