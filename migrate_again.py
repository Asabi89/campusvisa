import os
import re
import shutil

src_dir = 'c:/Users/admin/Documents/project/campusVisa/NextStepConsulting/'
dest_dir = 'c:/Users/admin/Documents/project/campusVisa/templates/nextstep/'

os.makedirs(dest_dir, exist_ok=True)

files = {
    'home': ('index.html', 'home_nextstep.html'),
    'campus_france': ('campus-france.html', 'campus_france_nextstep.html'),
    'contact': ('contact.html', 'contact_nextstep.html'),
    'faq': ('faq.html', 'faq_nextstep.html'),
    'mentions_legales': ('mentions-legales.html', 'mentions_legales_nextstep.html'),
}

for key, (src_name, dest_name) in files.items():
    with open(src_dir + src_name, 'r', encoding='utf-8') as f:
        src_html = f.read()
    
    match = re.search(r'</header>\s*(.*?)\s*<!-- Footer -->', src_html, re.DOTALL)
    if match:
        content = match.group(1)
    else:
        match2 = re.search(r'</header>\s*(.*?)\s*<footer', src_html, re.DOTALL)
        content = match2.group(1) if match2 else ""

    content = re.sub(r'src="assets/([^"]+)"', r'src="{% static \'assets/\1\' %}"', content)
    
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

