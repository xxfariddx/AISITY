from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import UserProfile


class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    father_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Father\'s Name'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'


class RoleSelectionForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role']
        widgets = {
            'role': forms.RadioSelect(),
        }


class StudyLocationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['study_location']
        widgets = {
            'study_location': forms.RadioSelect(),
        }


class ProfileInfoForm(forms.ModelForm):
    """Update User first/last name."""
    first_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )

    class Meta:
        model = UserProfile
        fields = ['father_name', 'subject_group']
        widgets = {
            'father_name': forms.TextInput(attrs={'placeholder': "Father's Name"}),
            'subject_group': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class ScoresForm(forms.ModelForm):
    """User academic scores."""
    class Meta:
        model = UserProfile
        fields = ['ielts_score', 'toefl_score', 'sat_score', 'dim_score']
        widgets = {
            'ielts_score': forms.NumberInput(attrs={'placeholder': '0.0 – 9.0', 'step': '0.5', 'min': '0', 'max': '9'}),
            'toefl_score': forms.NumberInput(attrs={'placeholder': '0 – 120', 'min': '0', 'max': '120'}),
            'sat_score':   forms.NumberInput(attrs={'placeholder': '400 – 1600', 'min': '400', 'max': '1600'}),
            'dim_score':   forms.NumberInput(attrs={'placeholder': '0 – 700', 'min': '0', 'max': '700'}),
        }
        labels = {
            'ielts_score': 'IELTS Score',
            'toefl_score': 'TOEFL Score',
            'sat_score':   'SAT Score',
            'dim_score':   'DİM Score',
        }

    def clean_ielts_score(self):
        val = self.cleaned_data.get('ielts_score')
        if val is not None and not (0 <= float(val) <= 9):
            raise ValidationError('IELTS score must be between 0.0 and 9.0.')
        return val

    def clean_toefl_score(self):
        val = self.cleaned_data.get('toefl_score')
        if val is not None and not (0 <= val <= 120):
            raise ValidationError('TOEFL score must be between 0 and 120.')
        return val

    def clean_sat_score(self):
        val = self.cleaned_data.get('sat_score')
        if val is not None and not (400 <= val <= 1600):
            raise ValidationError('SAT score must be between 400 and 1600.')
        return val

    def clean_dim_score(self):
        val = self.cleaned_data.get('dim_score')
        if val is not None and not (0 <= val <= 700):
            raise ValidationError('DİM score must be between 0 and 700.')
        return val
