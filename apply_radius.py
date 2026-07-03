import os

files = ['index.html', 'campus-france.html', 'contact.html']

css_rule = '''
        /* Apply 11px border radius */
        a.bg-gold, a.bg-marine, button.bg-marine,
        img.object-cover, .absolute.inset-0.transform,
        .bg-white.p-8, .bg-marine.p-8, .bg-light.p-8,
        .w-12.h-12, .w-16.h-16, .w-10.h-10,
        input, select, textarea {
            border-radius: 11px !important;
        }
'''

for file in files:
    path = os.path.join('NextStepConsulting', file)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '/* Apply 11px border radius */' not in content:
            content = content.replace('body { font-family: \\'Inter\\', sans-serif; }', 
                                      'body { font-family: \\'Inter\\', sans-serif; }' + css_rule)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        print(f"Updated {file}")
