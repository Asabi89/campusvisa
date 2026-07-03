import re

files = {
    'home': ('index.html', 'home_nextstep.html'),
    'campus_france': ('campus-france.html', 'campus_france_nextstep.html'),
    'contact': ('contact.html', 'contact_nextstep.html'),
    'faq': ('faq.html', 'faq_nextstep.html'),
    'mentions_legales': ('mentions-legales.html', 'mentions_legales_nextstep.html'),
}

src_dir = 'c:/Users/admin/Documents/project/campusVisa/NextStepConsulting/'
dest_dir = 'c:/Users/admin/Documents/project/campusVisa/templates/nextstep/'

for key, (src_name, dest_name) in files.items():
    with open(src_dir + src_name, 'r', encoding='utf-8') as f:
        src_html = f.read()
    
    # Extract content between </header> and <!-- Footer -->
    match = re.search(r'</header>\s*(.*?)\s*<!-- Footer -->', src_html, re.DOTALL)
    if match:
        content = match.group(1)
    else:
        # Fallback if no footer comment
        match2 = re.search(r'</header>\s*(.*?)\s*<footer', src_html, re.DOTALL)
        content = match2.group(1) if match2 else ""

    # Fix image links to use Django static tags
    content = re.sub(r'src="assets/([^"]+)"', r'src="{% static \'assets/\1\' %}"', content)
    
    # Extract scripts
    script_match = re.search(r'<script>(.*?)</script>', src_html, re.DOTALL)
    extra_js = ""
    if script_match:
        # Don't include the mobile menu script because it's already in base_nextstep.html!
        # Mobile menu script has 'mobile-menu-btn'
        script_content = script_match.group(1)
        if 'mobile-menu-btn' in script_content:
            # Maybe there are multiple script tags, or they are merged.
            # Let's extract ALL script tags from src
            pass

    # Actually, let's just get all script tags that are NOT the mobile menu toggle
    scripts = re.findall(r'<script>(.*?)</script>', src_html, re.DOTALL)
    js_content = ""
    for s in scripts:
        if 'mobile-menu-btn' not in s:
            js_content += "\n<script>\n" + s.strip() + "\n</script>\n"

    new_html = "{% extends 'base_nextstep.html' %}\n{% load static %}\n\n{% block content %}\n"
    new_html += content + "\n{% endblock %}\n\n"
    if js_content.strip():
        new_html += "{% block extra_js %}\n" + js_content + "\n{% endblock %}\n"
        
    with open(dest_dir + dest_name, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"Migrated {src_name} to {dest_name}")

