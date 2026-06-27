import urllib.request
import re

try:
    url = 'https://www.indiavotes.com/'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', html, re.IGNORECASE)
    print('Found bihar links:', list(set([l for l in links if 'bihar' in l.lower()])))
    print('Found assembly links:', list(set([l for l in links if 'assembly' in l.lower()])))
    print('Found state links:', list(set([l for l in links if 'state' in l.lower()])))
    print('Found ac links:', list(set([l for l in links if 'ac/' in l.lower()])))
except Exception as e:
    print('Error:', e)
