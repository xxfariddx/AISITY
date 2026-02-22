from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import University, Faculty, MyUniversity, Review, RankEntry
from .forms import ReviewForm
from accounts.models import UserProfile


def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


@login_required
def home_view(request):
    profile = get_or_create_profile(request.user)

    if not profile.is_profile_complete():
        return redirect('role_select')

    universities = University.objects.all()

    if profile.study_location == 'azerbaijan':
        universities = universities.filter(country__iexact='Azerbaijan')
    elif profile.study_location == 'abroad':
        universities = universities.exclude(country__iexact='Azerbaijan')

    # Basic filters
    search       = request.GET.get('search', '').strip()
    degree_level = request.GET.get('degree_level', '').strip()
    country      = request.GET.get('country', '').strip()
    min_fee      = request.GET.get('min_fee', '').strip()
    max_fee      = request.GET.get('max_fee', '').strip()

    # Advanced filters
    has_scholarship  = request.GET.get('has_scholarship', '').strip()
    has_dormitory    = request.GET.get('has_dormitory', '').strip()
    match_my_scores  = request.GET.get('match_my_scores', '').strip()
    sort_by          = request.GET.get('sort_by', '').strip()

    if search:
        universities = universities.filter(name__icontains=search)
    if degree_level:
        universities = universities.filter(Q(degree_level=degree_level) | Q(degree_level='both'))
    if country:
        universities = universities.filter(country__icontains=country)
    if min_fee:
        try:
            universities = universities.filter(tuition_fee__gte=float(min_fee))
        except ValueError:
            pass
    if max_fee:
        try:
            universities = universities.filter(tuition_fee__lte=float(max_fee))
        except ValueError:
            pass
    if has_scholarship == '1':
        universities = universities.exclude(scholarships='')
    if has_dormitory == '1':
        universities = universities.filter(dormitory_available=True)

    # Match my scores: filter out universities whose IELTS/SAT requirement exceeds user's score
    if match_my_scores == '1':
        if profile.ielts_score is not None:
            universities = universities.filter(
                Q(ielts_required=False) | Q(ielts_score__lte=profile.ielts_score)
            )
        if profile.sat_score is not None:
            universities = universities.filter(
                Q(sat_required=False) | Q(sat_score__lte=profile.sat_score)
            )

    # Sorting
    if sort_by == 'fee_asc':
        universities = universities.order_by('tuition_fee')
    elif sort_by == 'fee_desc':
        universities = universities.order_by('-tuition_fee')
    elif sort_by == 'qs_ranking':
        universities = universities.order_by('qs_ranking')
    elif sort_by == 'name':
        universities = universities.order_by('name')

    saved_ids = set(
        MyUniversity.objects.filter(user=request.user).values_list('university_id', flat=True)
    )

    all_countries = University.objects.values_list('country', flat=True).distinct().order_by('country')

    context = {
        'universities': universities,
        'saved_ids': saved_ids,
        'search': search,
        'degree_level': degree_level,
        'country': country,
        'min_fee': min_fee,
        'max_fee': max_fee,
        'has_scholarship': has_scholarship,
        'has_dormitory': has_dormitory,
        'match_my_scores': match_my_scores,
        'sort_by': sort_by,
        'all_countries': all_countries,
        'profile': profile,
    }
    return render(request, 'universities/home.html', context)


@login_required
def university_detail_view(request, pk):
    university = get_object_or_404(University, pk=pk)
    faculties = university.faculties.all()
    is_saved = MyUniversity.objects.filter(user=request.user, university=university).exists()

    # Review filtering / sorting
    filter_rating    = request.GET.get('filter_rating', '').strip()
    filter_recommend = request.GET.get('filter_recommend', '').strip()
    filter_verified  = request.GET.get('filter_verified', '').strip()
    sort_reviews     = request.GET.get('sort_reviews', 'newest').strip()

    reviews_qs = Review.objects.filter(university=university).select_related('user')

    if filter_rating:
        try:
            reviews_qs = reviews_qs.filter(rating=int(filter_rating))
        except ValueError:
            pass
    if filter_recommend in ('yes', 'no'):
        reviews_qs = reviews_qs.filter(recommend=filter_recommend)
    if filter_verified == '1':
        reviews_qs = reviews_qs.filter(is_verified=True)

    if sort_reviews == 'highest':
        reviews_qs = reviews_qs.order_by('-rating', '-created_at')
    elif sort_reviews == 'lowest':
        reviews_qs = reviews_qs.order_by('rating', '-created_at')
    else:
        reviews_qs = reviews_qs.order_by('-created_at')

    # Aggregate stats
    all_reviews   = Review.objects.filter(university=university)
    review_count  = all_reviews.count()
    avg_rating    = all_reviews.aggregate(avg=Avg('rating'))['avg']
    avg_rating    = round(avg_rating, 1) if avg_rating else None
    recommend_pct = None
    if review_count:
        yes_count = all_reviews.filter(recommend='yes').count()
        recommend_pct = round(yes_count / review_count * 100)

    # Rating breakdown (5 down to 1)
    rating_breakdown = []
    for star in range(5, 0, -1):
        count = all_reviews.filter(rating=star).count()
        pct = round(count / review_count * 100) if review_count else 0
        rating_breakdown.append({'star': star, 'count': count, 'pct': pct})

    # The current user's existing review (if any)
    user_review = Review.objects.filter(university=university, user=request.user).first()

    return render(request, 'universities/university_detail.html', {
        'university': university,
        'faculties': faculties,
        'is_saved': is_saved,
        'reviews': reviews_qs,
        'review_count': review_count,
        'avg_rating': avg_rating,
        'recommend_pct': recommend_pct,
        'rating_breakdown': rating_breakdown,
        'user_review': user_review,
        'filter_rating': filter_rating,
        'filter_recommend': filter_recommend,
        'filter_verified': filter_verified,
        'sort_reviews': sort_reviews,
    })


@login_required
def add_university_view(request, pk):
    university = get_object_or_404(University, pk=pk)
    obj, created = MyUniversity.objects.get_or_create(user=request.user, university=university)
    if created:
        messages.success(request, f'"{university.name}" has been added to your list!')
    else:
        messages.info(request, f'"{university.name}" is already in your list.')
    next_url = request.GET.get('next', '')
    if next_url == 'university_detail':
        return redirect('university_detail', pk=pk)
    return redirect('home')


@login_required
def remove_university_view(request, pk):
    university = get_object_or_404(University, pk=pk)
    MyUniversity.objects.filter(user=request.user, university=university).delete()
    messages.success(request, f'"{university.name}" removed from your list.')
    next_url = request.GET.get('next', '')
    if next_url == 'university_detail':
        return redirect('university_detail', pk=pk)
    if next_url == 'home':
        return redirect('home')
    return redirect('my_universities')


@login_required
def my_universities_view(request):
    saved = MyUniversity.objects.filter(user=request.user).select_related('university')
    return render(request, 'universities/my_universities.html', {'saved': saved})


@login_required
def add_review_view(request, pk):
    university = get_object_or_404(University, pk=pk)

    # Prevent duplicate reviews
    existing = Review.objects.filter(university=university, user=request.user).first()
    if existing:
        messages.info(request, 'You have already submitted a review for this university. You can edit it below.')
        return redirect('university_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.university = university
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been submitted successfully!')
            return redirect('university_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm()

    return render(request, 'universities/review_form.html', {
        'form': form,
        'university': university,
        'action': 'Submit',
    })


@login_required
def edit_review_view(request, pk, review_pk):
    university = get_object_or_404(University, pk=pk)
    review = get_object_or_404(Review, pk=review_pk, university=university, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated.')
            return redirect('university_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'universities/review_form.html', {
        'form': form,
        'university': university,
        'review': review,
        'action': 'Update',
    })


@login_required
def delete_review_view(request, pk, review_pk):
    university = get_object_or_404(University, pk=pk)
    review = get_object_or_404(Review, pk=review_pk, university=university, user=request.user)

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted.')
        return redirect('university_detail', pk=pk)

    return render(request, 'universities/review_confirm_delete.html', {
        'university': university,
        'review': review,
    })


# ──────────────────────────────────────────────────────────────
#  RANK YOURSELF
# ──────────────────────────────────────────────────────────────

@login_required
def rank_yourself_view(request):
    """Page where users drag-and-drop faculties to build their personal ranking."""
    # All faculties grouped by university, with payment info
    all_faculties = (
        Faculty.objects
        .select_related('university')
        .order_by('university__name', 'name')
    )

    # User's existing saved ranking
    saved_entries = (
        RankEntry.objects
        .filter(user=request.user)
        .select_related('faculty__university')
        .order_by('position')
    )
    saved_faculty_ids = [e.faculty_id for e in saved_entries]

    # Filter controls
    search_q    = request.GET.get('q', '').strip()
    filter_uni  = request.GET.get('uni', '').strip()
    filter_pay  = request.GET.get('pay', '').strip()   # 'state' | 'paid' | ''

    available = all_faculties
    if search_q:
        available = available.filter(
            Q(name__icontains=search_q) | Q(university__name__icontains=search_q)
        )
    if filter_uni:
        available = available.filter(university__pk=filter_uni)
    if filter_pay == 'state':
        available = available.filter(state_order_places__gt=0)
    elif filter_pay == 'paid':
        available = available.filter(tuition_paid__isnull=False)

    all_universities = University.objects.order_by('name')

    return render(request, 'universities/rank_yourself.html', {
        'available_faculties': available,
        'saved_entries': saved_entries,
        'saved_faculty_ids': saved_faculty_ids,
        'all_universities': all_universities,
        'search_q': search_q,
        'filter_uni': filter_uni,
        'filter_pay': filter_pay,
    })


@login_required
@require_POST
def save_ranking(request):
    """AJAX: receive ordered list of faculty IDs and save as RankEntry rows."""
    try:
        data = json.loads(request.body)
        faculty_ids = data.get('faculty_ids', [])
    except Exception:
        return JsonResponse({'error': 'Invalid data'}, status=400)

    if not isinstance(faculty_ids, list):
        return JsonResponse({'error': 'faculty_ids must be a list'}, status=400)

    # Validate all IDs exist
    valid_ids = set(Faculty.objects.filter(pk__in=faculty_ids).values_list('pk', flat=True))

    # Delete existing ranking for this user
    RankEntry.objects.filter(user=request.user).delete()

    # Recreate in new order
    entries = []
    for pos, fid in enumerate(faculty_ids, start=1):
        if fid in valid_ids:
            entries.append(RankEntry(user=request.user, faculty_id=fid, position=pos))
    RankEntry.objects.bulk_create(entries)

    return JsonResponse({'status': 'ok', 'saved': len(entries)})
