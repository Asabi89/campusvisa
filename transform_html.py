import re
import os

base_path = r'c:\Users\admin\Documents\project\campusVisa\visnextstep'
django_pages = r'c:\Users\admin\Documents\project\campusVisa\templates\pages'

mappings = {
    'index.html': 'home.html',
    'tarifs.html': 'pricing.html',
    'faq.html': 'faq.html',
    'contact.html': 'contact.html',
}

for source_file, target_file in mappings.items():
    source_path = os.path.join(base_path, source_file)
    target_path = os.path.join(django_pages, target_file)
    
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract content between </header> and <footer>
    match = re.search(r'</header>\s*(.*?)\s*<footer', content, re.DOTALL | re.IGNORECASE)
    if not match:
        print(f"Could not find </header> or <footer in {source_file}")
        continue
        
    main_content = match.group(1)
    
    # 1. Replace frenchBlue with visaRed
    main_content = main_content.replace('frenchBlue', 'visaRed')
    
    # 2. Replace static assets links
    # Typical: src="assets/icon_folder.png" -> src="{% static 'images/icon_folder.png' %}"
    # or href="assets/something"
    main_content = re.sub(
        r'([src|href]+)="assets/([^"]+)"',
        r'\1="{% static \'images/\2\' %}"',
        main_content
    )
    
    # 3. Replace html page links with Django url tags if possible
    # We can just change tarifs.html to {% url 'pages:pricing' %} etc.
    main_content = main_content.replace('href="index.html"', 'href="{% url \'pages:home\' %}"')
    main_content = main_content.replace('href="tarifs.html"', 'href="{% url \'pages:pricing\' %}"')
    main_content = main_content.replace('href="faq.html"', 'href="{% url \'pages:faq\' %}"')
    main_content = main_content.replace('href="contact.html"', 'href="{% url \'pages:contact\' %}"')
    
    # Also some might have href="#" for login/signup, but we leave it as is or replace with real urls if obvious.
    
    # 4. Wrap with Django blocks
    final_content = "{% extends 'base.html' %}\n{% load static %}\n\n{% block content %}\n\n" + main_content + "\n\n{% endblock %}\n"
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"Processed {source_file} -> {target_file}")
