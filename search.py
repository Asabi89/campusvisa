import json
import re

log_path = r"C:\Users\admin\.gemini\antigravity-ide\brain\d1fd3f4b-22f7-453c-9f58-60e791ae63ca\.system_generated\logs\transcript.jsonl"
try:
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if 'home.html' in line and 'templates/pages/home.html' not in line: # actually let's just dump lines with 'pages/home.html'
                pass
            
            if 'pages/home.html' in line:
                data = json.loads(line)
                # Print just a snippet
                content = str(data)[:300]
                print("FOUND:", content)
except Exception as e:
    print(e)
