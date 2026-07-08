import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
django.setup()

from apps.pages.models import PricingPageSettings, PricingPlan, PricingFeature

# Create page settings
settings = PricingPageSettings.get_solo()
settings.title = "Un tarif transparent.<br/>Zéro surprise."
settings.subtitle = "Choisissez l'offre qui correspond à vos besoins et bénéficiez de l'accompagnement idéal pour vos études en France."
settings.cta_title = "Encore des questions sur nos tarifs ?"
settings.cta_subtitle = "Notre équipe est là pour vous guider vers la meilleure formule pour votre profil."
settings.cta_button_text = "Contacter un conseiller"
settings.cta_button_link = "pages:contact"
settings.save()

# Create Plans
plans_data = [
    {
        'name': 'Essentiel',
        'description': 'Pour les étudiants autonomes qui souhaitent vérifier leur dossier.',
        'price': '49€',
        'button_text': 'Choisir Essentiel',
        'button_link': '#',
        'is_popular': False,
        'features_list': '- Accès à la plateforme (Coffre-fort)\n- Roadmap personnalisée\n- Relecture de 2 documents\nx Chat en temps réel',
        'order': 1
    },
    {
        'name': 'Premium',
        'description': "L'accompagnement complet avec coaching de A à Z.",
        'price': '199€',
        'button_text': 'Commencer Premium',
        'button_link': '#',
        'is_popular': True,
        'features_list': '- Tout de l\'offre Essentiel\n- Validation illimitée des documents\n- Chat en direct 7j/7\n- 2 entretiens blancs en visio',
        'order': 2
    },
    {
        'name': 'Excellence',
        'description': 'Pour les cas complexes (refus antérieur, réorientation).',
        'price': 'Sur devis',
        'button_text': 'Nous contacter',
        'button_link': '/contact/',
        'is_popular': False,
        'features_list': '- Tout de l\'offre Premium\n- Accompagnement prioritaire VIP\n- Recours gracieux / contentieux',
        'order': 3
    }
]

for p in plans_data:
    plan, created = PricingPlan.objects.get_or_create(name=p['name'], defaults=p)
    if not created:
        for k, v in p.items():
            setattr(plan, k, v)
        plan.save()

# Create Features
features_data = [
    {
        'name': 'Accès au Dashboard',
        'basic_value': 'Oui',
        'premium_value': 'Oui',
        'excellence_value': 'Oui',
        'order': 1
    },
    {
        'name': 'Relecture Lettre de Motivation',
        'basic_value': '1 seule fois',
        'premium_value': 'Oui',
        'excellence_value': 'Oui',
        'order': 2
    },
    {
        'name': 'Chat avec un conseiller',
        'basic_value': 'Non',
        'premium_value': 'Oui',
        'excellence_value': 'Oui',
        'order': 3
    },
    {
        'name': "Simulation d'entretien vidéo",
        'basic_value': 'Non',
        'premium_value': '2 séances',
        'excellence_value': 'Illimité',
        'order': 4
    }
]

for f in features_data:
    feat, created = PricingFeature.objects.get_or_create(name=f['name'], defaults=f)
    if not created:
        for k, v in f.items():
            setattr(feat, k, v)
        feat.save()

print("Tarifs data populated successfully!")
