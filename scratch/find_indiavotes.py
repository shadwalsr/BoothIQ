import urllib.request
import re

try:
    url = 'https://www.indiavotes.com/state'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    
    bihar_links = re.findall(r'href=[\'"]([^\'"]*bihar[^\'"]*)[\'"]', html, re.IGNORECASE)
    print('Found links for Bihar:', list(set(bihar_links)))
except Exception as e:
    print('Error:', e)
