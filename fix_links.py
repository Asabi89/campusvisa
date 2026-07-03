import os
import re

path = r'c:\Users\admin\Documents\project\campusVisa\templates\nextstep\home_nextstep.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'(<a\s+href=")\{% url \'nextstep:campus_france\' %\}(.*?>\s*Étudier en France)', r'\1{% url \'pages:home\' %}\2', content)
content = re.sub(r'(<a\s+href=")\{% url \'nextstep:campus_france\' %\}(.*?>\s*Découvrir l\'accompagnement)', r'\1{% url \'pages:home\' %}\2', content)
content = re.sub(r'(<a\s+href=")\{% url \'nextstep:campus_france\' %\}(.*?<div[^>]*>.*?Mobilité Internationale)', r'\1{% url \'pages:home\' %}\2', content, flags=re.DOTALL)
content = re.sub(r'(<a\s+href=")\{% url \'nextstep:campus_france\' %\}(.*?>\s*Campus France)', r'\1{% url \'pages:home\' %}\2', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
