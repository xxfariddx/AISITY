from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import SignupForm, RoleSelectionForm, StudyLocationForm, ProfileInfoForm, ScoresForm
from .models import UserProfile


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            UserProfile.objects.create(
                user=user,
                father_name=form.cleaned_data.get('father_name', '')
            )
            login(request, user)
            return redirect('role_select')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.is_profile_complete():
                return redirect('role_select')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def role_select_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('study_location')
    else:
        form = RoleSelectionForm(instance=profile)
    return render(request, 'accounts/role_select.html', {'form': form})


@login_required
def study_location_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = StudyLocationForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = StudyLocationForm(instance=profile)
    return render(request, 'accounts/study_location.html', {'form': form})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'info':
            info_form = ProfileInfoForm(request.POST, instance=profile, user=request.user)
            scores_form = ScoresForm(instance=profile)
            if info_form.is_valid():
                info_form.save()
                messages.success(request, 'Personal information updated successfully.')
                return redirect('profile')
        elif action == 'scores':
            info_form = ProfileInfoForm(instance=profile, user=request.user)
            scores_form = ScoresForm(request.POST, instance=profile)
            if scores_form.is_valid():
                scores_form.save()
                messages.success(request, 'Academic scores saved successfully.')
                return redirect('profile')
        else:
            info_form = ProfileInfoForm(instance=profile, user=request.user)
            scores_form = ScoresForm(instance=profile)
    else:
        info_form = ProfileInfoForm(instance=profile, user=request.user)
        scores_form = ScoresForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'info_form': info_form,
        'scores_form': scores_form,
        'profile': profile,
    })
