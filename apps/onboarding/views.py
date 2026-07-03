from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import OnboardingResponse

SCORING_MATRIX = {
    'passport_status': {
        'yes':        {'basic': 3, 'standard': 1, 'premium': 0},
        'in_process': {'basic': 1, 'standard': 3, 'premium': 1},
        'no':         {'basic': 0, 'standard': 1, 'premium': 3},
    },
    'education_level': {
        'master':      {'basic': 2, 'standard': 2, 'premium': 1},
        'bachelor':    {'basic': 1, 'standard': 2, 'premium': 2},
        'high_school': {'basic': 0, 'standard': 1, 'premium': 3},
    },
    'admission_status': {
        'admitted':    {'basic': 3, 'standard': 1, 'premium': 0},
        'applied':     {'basic': 1, 'standard': 3, 'premium': 1},
        'not_applied': {'basic': 0, 'standard': 1, 'premium': 3},
    },
    'campus_france_account': {
        'yes': {'basic': 3, 'standard': 1, 'premium': 0},
        'no':  {'basic': 0, 'standard': 1, 'premium': 3},
    },
    'visa_support': {
        'none':   {'basic': 3, 'standard': 0, 'premium': 0},
        'review': {'basic': 1, 'standard': 3, 'premium': 1},
        'full':   {'basic': 0, 'standard': 1, 'premium': 3},
    },
    'financial_situation': {
        'own_funds': {'basic': 2, 'standard': 2, 'premium': 1},
        'sponsor':   {'basic': 1, 'standard': 2, 'premium': 2},
        'not_ready': {'basic': 0, 'standard': 1, 'premium': 3},
    },
    'timeline': {
        'more_6':  {'basic': 3, 'standard': 2, 'premium': 0},
        '3_to_6':  {'basic': 1, 'standard': 3, 'premium': 1},
        'less_3':  {'basic': 0, 'standard': 1, 'premium': 3},
    },
}

MAX_SCORE = 21

PLAN_PRICES = {
    'basic': 49,
    'standard': 149,
    'premium': 299,
}


def _get_minimum_plan(response):
    """Determine the minimum plan based on critical factors.
    Returns 'basic', 'standard', or 'premium'."""

    # --- Premium obligatoire ---
    # Assistance visa complete → ne peut pas etre gere par Basic/Standard
    if response.visa_support == 'full':
        return 'premium'
    # Delai court + pas encore pret sur un critere cle
    if response.timeline == 'less_3' and response.admission_status == 'not_applied':
        return 'premium'
    if response.timeline == 'less_3' and response.passport_status == 'no':
        return 'premium'
    if response.timeline == 'less_3' and response.campus_france_account == 'no':
        return 'premium'
    # Cumul de lacunes (3+ reponses critiques)
    critical_count = sum([
        response.passport_status == 'no',
        response.admission_status == 'not_applied',
        response.campus_france_account == 'no',
        response.financial_situation == 'not_ready',
    ])
    if critical_count >= 3:
        return 'premium'

    # --- Standard minimum ---
    if response.visa_support == 'review':
        return 'standard'
    if response.timeline == 'less_3':
        return 'standard'
    if response.campus_france_account == 'no' and response.admission_status == 'not_applied':
        return 'standard'
    if response.financial_situation == 'not_ready':
        return 'standard'
    if critical_count >= 2:
        return 'standard'

    return 'basic'


def _calculate_scores(response):
    basic = standard = premium = 0
    for field, options in SCORING_MATRIX.items():
        answer = getattr(response, field, '')
        if answer in options:
            basic += options[answer]['basic']
            standard += options[answer]['standard']
            premium += options[answer]['premium']

    response.basic_score = round(basic / MAX_SCORE * 100)
    response.standard_score = round(standard / MAX_SCORE * 100)
    response.premium_score = round(premium / MAX_SCORE * 100)

    # Apply critical overrides
    minimum = _get_minimum_plan(response)
    plan_rank = {'basic': 0, 'standard': 1, 'premium': 2}

    scores = {
        'basic': response.basic_score,
        'standard': response.standard_score,
        'premium': response.premium_score,
    }
    score_winner = max(scores, key=scores.get)

    # Use the higher of: score-based winner or critical minimum
    if plan_rank[minimum] > plan_rank[score_winner]:
        response.recommended_plan = minimum
    else:
        response.recommended_plan = score_winner

    response.needs_assistance = max(scores.values()) < 30
    response.completed = True
    response.save()


@login_required
def questionnaire(request):
    if request.user.has_completed_onboarding:
        return redirect('onboarding:result')

    try:
        response = OnboardingResponse.objects.get(user=request.user)
        if response.completed:
            return redirect('onboarding:result')
    except OnboardingResponse.DoesNotExist:
        pass

    if request.method == 'POST':
        response, _ = OnboardingResponse.objects.get_or_create(user=request.user)
        fields = [
            'passport_status', 'education_level', 'admission_status',
            'campus_france_account', 'visa_support', 'financial_situation',
            'timeline',
        ]
        for field in fields:
            setattr(response, field, request.POST.get(field, ''))
        response.save()
        _calculate_scores(response)

        request.user.has_completed_onboarding = True
        request.user.save(update_fields=['has_completed_onboarding'])
        return redirect('onboarding:result')

    return render(request, 'onboarding/questionnaire.html')


@login_required
def reset(request):
    OnboardingResponse.objects.filter(user=request.user).delete()
    request.user.has_completed_onboarding = False
    request.user.save(update_fields=['has_completed_onboarding'])
    return redirect('onboarding:questionnaire')


@login_required
def result(request):
    try:
        response = OnboardingResponse.objects.get(user=request.user)
    except OnboardingResponse.DoesNotExist:
        return redirect('onboarding:questionnaire')

    if not response.completed:
        return redirect('onboarding:questionnaire')

    all_plans = [
        {'name': 'Premium', 'slug': 'premium', 'score': response.premium_score, 'price': PLAN_PRICES['premium']},
        {'name': 'Standard', 'slug': 'standard', 'score': response.standard_score, 'price': PLAN_PRICES['standard']},
        {'name': 'Basique', 'slug': 'basic', 'score': response.basic_score, 'price': PLAN_PRICES['basic']},
    ]

    # Recommended plan first, then the rest sorted by score descending
    recommended = [p for p in all_plans if p['slug'] == response.recommended_plan]
    others = sorted(
        [p for p in all_plans if p['slug'] != response.recommended_plan],
        key=lambda p: p['score'],
        reverse=True,
    )
    plans = recommended + others

    recommended_name = plans[0]['name']

    reasons = []
    if response.visa_support == 'full':
        reasons.append("vous avez besoin d'une assistance visa complete")
    if response.campus_france_account == 'no':
        reasons.append("vous n'avez pas encore de compte Campus France")
    if response.timeline == 'less_3':
        reasons.append("votre delai est court (moins de 3 mois)")
    if response.admission_status == 'not_applied':
        reasons.append("vous n'avez pas encore postule")
    if response.passport_status == 'no':
        reasons.append("vous n'avez pas encore de passeport")
    if response.financial_situation == 'not_ready':
        reasons.append("votre situation financiere necessite un accompagnement")

    explanation = ''
    if reasons:
        explanation = f"Nous recommandons le plan {recommended_name} car {', '.join(reasons[:3])}."

    return render(request, 'onboarding/result.html', {
        'response': response,
        'plans': plans,
        'explanation': explanation,
    })
