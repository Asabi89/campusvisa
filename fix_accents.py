import os
import re

templates_dir = r'c:\Users\admin\Documents\project\campusVisa\templates'

replacements = {
    r'\betudier\b': 'étudier',
    r'\bDemarrer\b': 'Démarrer',
    r'\bdemarrer\b': 'démarrer',
    r'\bA propos\b': 'À propos',
    r'\bca marche\b': 'ça marche',
    r'\bca \b': 'ça ',
    r'\betape\b': 'étape',
    r'\bEtape\b': 'Étape',
    r'\bpersonnalise\b': 'personnalisé',
    r'\bpersonalise\b': 'personnalisé',
    r'\bfonctionnalites\b': 'fonctionnalités',
    r'\bFonctionnalites\b': 'Fonctionnalités',
    r'\bDecouvrir\b': 'Découvrir',
    r'\bdecouvrir\b': 'découvrir',
    r'\bCreez\b': 'Créez',
    r'\brealite\b': 'réalité',
    r'\bnumero\b': 'numéro',
    r'\bNumero\b': 'Numéro',
    r'\bdepot\b': 'dépôt',
    r'\ba chaque etape\b': 'à chaque étape',
    r'\ba l\'obtention\b': 'à l\'obtention',
    r'\bCompletez\b': 'Complétez',
    r'\badapte\b': 'adapté',
    r'\bnecessite\b': 'nécessite',
    r'\beviter\b': 'éviter',
    r'\bconcretes\b': 'concrètes',
    r'\bprecedente\b': 'précédente',
    r'\bparametres\b': 'paramètres',
    r'\bevaluer\b': 'évaluer',
    r'\bEvaluer\b': 'Évaluer',
    r'\bcriteres\b': 'critères',
    r'\bCriteres\b': 'Critères',
    r'\brepondez\b': 'répondez',
    r'\btres\b': 'très',
    r'\bTres\b': 'Très',
    r'\bdeja\b': 'déjà',
    r'\bDeja\b': 'Déjà',
    r'\bmeme\b': 'même',
    r'\bbientot\b': 'bientôt',
    r'\bAccedez\b': 'Accédez',
    r'\baccedez\b': 'accédez',
    r'\bCreer\b': 'Créer',
    r'\bcreer\b': 'créer',
    r'\benvoye\b': 'envoyé',
    r'\bCree \b': 'Crée ',
    r'\bcree \b': 'crée ',
    r'\bcreneau\b': 'créneau',
    r'\bcreneaux\b': 'créneaux',
    r'\bRefuse\b': 'Refusé',
    r'\brefuse\b': 'refusé',
    r'\btelecharger\b': 'télécharger',
    r'\bre-telecharger\b': 're-télécharger',
    r'\btelechargé\b': 'téléchargé',
    r'\btelecharge\b': 'télécharge',
    r'\betudes\b': 'études',
    r'\bEtudes\b': 'Études',
    r'\bpreparer\b': 'préparer',
    r'\bbeneficiez\b': 'bénéficiez',
    r'\bdecouvrez\b': 'découvrez',
    r'\bverifie\b': 'vérifié',
    r'\bVerifie\b': 'Vérifié',
    r'\bdemarche\b': 'démarche',
    r'\bdemarches\b': 'démarches',
    r'\betudiant\b': 'étudiant',
    r'\bEtudiant\b': 'Étudiant',
    r'\bRejete\b': 'Rejeté',
    r'\brejete\b': 'rejeté',
    r'\bcloturer\b': 'clôturer',
    r'\baccepte\b': 'accepté',
    r'\bAccepte\b': 'Accepté',
    r'\btraite\b': 'traité',
    r'\bTraite\b': 'Traité',
    r'\breponse\b': 'réponse',
    r'\bevaluation\b': 'évaluation',
    r'\bfrancais\b': 'français',
    r'\betudiants\b': 'étudiants',
    r'\bEtudiants\b': 'Étudiants',
    r'\bdiplome\b': 'diplôme',
    r'\bverifier\b': 'vérifier',
    r'\bprenom\b': 'prénom',
    r'\bacces\b': 'accès',
    r'\bsucces\b': 'succès',
    r'\betapes\b': 'étapes',
    r'\bEtapes\b': 'Étapes',
    r'\bprecedent\b': 'précédent',
    r'\btelechargez\b': 'téléchargez',
    r'\B a\b(?! href)(?! class)(?! id)(?! name)(?! type)(?! value)(?! for)(?! alt)(?! src)': ' à',
}

# Be safer with ' a ' mapping
safer_a_replacements = {
    r'\b a votre\b': ' à votre',
    r'\b a vos\b': ' à vos',
    r'\b a la\b': ' à la',
    r'\b a un\b': ' à un',
    r'\b a une\b': ' à une',
    r'\b a des\b': ' à des',
    r'\b a chaque\b': ' à chaque',
    r'\b a l\'': ' à l\'',
    r'\b a \b(?!href|class|id|name|type|value|for|alt|src|data|aria|xmlns|content|property|rel)': ' à ',
}

project_dir = r'c:\Users\admin\Documents\project\campusVisa'
exclude_dirs = {'venv', 'env', 'node_modules', '.git', '__pycache__', '.vscode'}

for root, dirs, files in os.walk(project_dir):
    # Exclude directories
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            for pattern, replacement in replacements.items():
                # Avoid touching ' a ' wildcard in the first pass
                if pattern.startswith(r'\B'):
                    continue
                content = re.sub(pattern, replacement, content)
                
            for pattern, replacement in safer_a_replacements.items():
                content = re.sub(pattern, replacement, content)
                
            # One special case 'ça ' without boundary issue for HTML tags
            content = content.replace(" Comment ca marche", " Comment ça marche")
            content = content.replace(" ca marche", " ça marche")
            content = content.replace(">ca<", ">ça<")
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {filepath}")
print("Done.")
