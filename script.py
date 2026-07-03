import os

folder = r'c:\Users\admin\Documents\project\campusVisa\templates\nextstep'

for file in os.listdir(folder):
    if file.endswith('.html'):
        filepath = os.path.join(folder, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("{% url 'pages:home' %}", "{% url 'pages:nextstep_home' %}")
        content = content.replace("{% url 'pages:faq' %}", "{% url 'pages:nextstep_faq' %}")
        content = content.replace("{% url 'pages:contact' %}", "{% url 'pages:nextstep_contact' %}")
        content = content.replace("{% url 'pages:mentions_legales' %}", "{% url 'pages:nextstep_mentions_legales' %}")
        content = content.replace("{% url 'pages:campus_france' %}", "{% url 'pages:nextstep_campus_france' %}")
        content = content.replace("{% extends 'base.html' %}", "{% extends 'base_nextstep.html' %}")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

# Also update base_nextstep.html
base_path = r'c:\Users\admin\Documents\project\campusVisa\templates\base_nextstep.html'
with open(base_path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("{% url 'pages:home' %}", "{% url 'pages:nextstep_home' %}")
content = content.replace("{% url 'pages:faq' %}", "{% url 'pages:nextstep_faq' %}")
content = content.replace("{% url 'pages:contact' %}", "{% url 'pages:nextstep_contact' %}")
content = content.replace("{% url 'pages:mentions_legales' %}", "{% url 'pages:nextstep_mentions_legales' %}")
content = content.replace("{% url 'pages:campus_france' %}", "{% url 'pages:nextstep_campus_france' %}")
with open(base_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated links for NextStep")
