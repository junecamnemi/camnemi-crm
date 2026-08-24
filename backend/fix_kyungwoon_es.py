import json, re
# Fix data.js: 경운대학교 es Kyungwoon -> KWU
with open('data.js', encoding='utf-8') as f:
    h = f.read()

# replace the es field for the 경운대학교 entry
old = '"en": "Kyungwoon University", "es": "Kyungwoon"'
new = '"en": "Kyungwoon University", "es": "KWU"'
count = h.count(old)
print('occurrences in data.js:', count)
h = h.replace(old, new)
with open('data.js', 'w', encoding='utf-8') as f:
    f.write(h)
print('data.js updated')
