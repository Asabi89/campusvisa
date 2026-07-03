import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.notifications.services import notify_staff
from apps.onboarding.views import PLAN_PRICES

from .models import Plan, Subscription


PLAN_FEATURES = {
    'basic': [
        'Guide Campus France',
        'Checklist documents',
        'Support par email',
    ],
    'standard': [
        'Revision des documents',
        'Suivi Campus France',
        'Chat avec conseiller',
        '3 reunions incluses',
    ],
    'premium': [
        'Accompagnement visa complet',
        'Inscription Campus France',
        'Preparation entretien',
        'Chat et reunions illimites',
        'Conseiller dedie',
    ],
}


@login_required
def checkout(request, slug):
    if hasattr(request.user, 'subscription') and request.user.subscription.status == 'active':
        return redirect('dashboard:overview')

    price = PLAN_PRICES.get(slug)
    if price is None:
        return redirect('onboarding:result')

    plan_names = {'basic': 'Basique', 'standard': 'Standard', 'premium': 'Premium'}

    context = {
        'plan_slug': slug,
        'plan_name': plan_names.get(slug, slug),
        'plan_price': price,
        'plan_features': PLAN_FEATURES.get(slug, []),
        'payment_methods': Subscription.PAYMENT_METHOD_CHOICES,
    }

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', '')
        phone_number = request.POST.get('phone_number', '').strip()

        if not payment_method:
            messages.error(request, 'Veuillez choisir un moyen de paiement.')
            return render(request, 'plans/checkout.html', context)

        if not phone_number:
            messages.error(request, 'Veuillez entrer votre numero de telephone.')
            return render(request, 'plans/checkout.html', context)

        # Get or create Plan in DB
        plan, _ = Plan.objects.get_or_create(
            slug=slug,
            defaults={
                'name': plan_names.get(slug, slug),
                'description': f'Plan {plan_names.get(slug, slug)} Visanextstep',
                'price': price,
                'features': PLAN_FEATURES.get(slug, []),
                'order': {'basic': 1, 'standard': 2, 'premium': 3}.get(slug, 0),
            },
        )

        # Create subscription (pending payment confirmation)
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={
                'plan': plan,
                'status': 'pending',
                'payment_method': payment_method,
                'phone_number': phone_number,
                'payment_reference': f'CV-{uuid.uuid4().hex[:8].upper()}',
            },
        )

        if not created:
            subscription.plan = plan
            subscription.payment_method = payment_method
            subscription.phone_number = phone_number
            subscription.payment_reference = f'CV-{uuid.uuid4().hex[:8].upper()}'
            subscription.status = 'pending'
            subscription.save()

        request.user.has_active_plan = True
        request.user.save(update_fields=['has_active_plan'])
        notify_staff(
            created_by=request.user,
            notification_type='staff_payment_pending',
            category='billing',
            priority='high',
            title='Paiement en attente',
            message=f'{request.user.email} a lance un paiement {payment_method} pour le plan {plan.name}.',
            link='/subscriptions/',
            payload={
                'student_id': request.user.id,
                'subscription_id': subscription.id,
                'payment_reference': subscription.payment_reference,
            },
        )

        return redirect('plans:confirmation', slug=slug)

    return render(request, 'plans/checkout.html', context)


@login_required
def confirmation(request, slug):
    try:
        subscription = request.user.subscription
    except Subscription.DoesNotExist:
        return redirect('onboarding:result')

    plan_names = {'basic': 'Basique', 'standard': 'Standard', 'premium': 'Premium'}
    method_names = dict(Subscription.PAYMENT_METHOD_CHOICES)

    return render(request, 'plans/confirmation.html', {
        'subscription': subscription,
        'plan_name': plan_names.get(slug, slug),
        'plan_price': PLAN_PRICES.get(slug, 0),
        'method_name': method_names.get(subscription.payment_method, ''),
    })

