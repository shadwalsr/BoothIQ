import urllib.request
import re
import json
import time
import os
from bs4 import BeautifulSoup

def clean_ac_name(name):
    return name.lower().replace('-', ' ').replace('_', ' ').strip()

try:
    url = 'https://www.indiavotes.com/vidhan-sabha/bihar/2020/'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    links = soup.find_all('a', href=re.compile(r'bihar/2020/.+'))
    constituencies = []
    for link in links:
        href = link['href']
        parts = href.split('/')
        if len(parts) >= 5 and parts[3] == '2020':
             ac_name_slug = parts[4]
             if ac_name_slug not in constituencies:
                 constituencies.append(ac_name_slug)
                 
    print('Found', len(constituencies), 'unique constituency links.')
    
    results = {}
    
    # Optional: Save partial progress to avoid losing data on crash
    output_file = os.path.join(os.path.dirname(__file__), 'indiavotes_results_2020.json')
    
    for i, slug in enumerate(constituencies):
        print(f'Scraping {i+1}/{len(constituencies)}: {slug}...')
        try:
            c_url = f'https://www.indiavotes.com/vidhan-sabha/bihar/2020/{slug}/'
            c_req = urllib.request.Request(c_url, headers={'User-Agent': 'Mozilla/5.0'})
            c_html = urllib.request.urlopen(c_req).read().decode('utf-8')
            c_soup = BeautifulSoup(c_html, 'html.parser')
            
            table = c_soup.find('table')
            if table:
                rows = table.find_all('tr')
                if len(rows) > 1:
                     cells = [td.text.strip() for td in rows[1].find_all(['th', 'td'])]
                     if len(cells) >= 3:
                         # Candidate name might have 'Winner' at the end
                         winner_name = cells[1].replace('Winner', '').strip()
                         party = cells[2]
                         results[clean_ac_name(slug)] = {'candidate': winner_name, 'party': party}
        except Exception as inner_e:
            print(f'  Failed to scrape {slug}: {inner_e}')
            
        # Write to file every 10 constituencies
        if i % 10 == 0:
             with open(output_file, 'w') as f:
                 json.dump(results, f, indent=2)
                 
        time.sleep(1) # Be nice to the server (1 request per second)
        
    # Final write
    with open(output_file, 'w') as f:
         json.dump(results, f, indent=2)
         
    print(f'Scraping complete. Wrote {len(results)} results to {output_file}')
        
except Exception as e:
    print('Error:', e)
