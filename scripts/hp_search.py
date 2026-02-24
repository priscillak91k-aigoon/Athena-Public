import urllib.request
import urllib.parse
import json

def search_healthpost(query):
    # HealthPost uses a standard Shopify/Searchspring implementation
    # We will just do a basic HTML search scrape since we know the products exist
    url = f"https://www.healthpost.co.nz/search?q={urllib.parse.quote(query)}"
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    )
    
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        # Very basic extraction - just look for product links
        links = []
        for line in html.split('\n'):
            if 'href="/p/' in line or 'href="/' in line and '-product' in line:
                # Extract href
                try:
                    start = line.index('href="') + 6
                    end = line.index('"', start)
                    link = line[start:end]
                    if link not in links and link.startswith('/'):
                        links.append(f"https://www.healthpost.co.nz{link}")
                except:
                    pass
        print(f"Results for '{query}':")
        for l in links[:3]:
            print(f"- {l}")
    except Exception as e:
        print(f"Error: {e}")

search_healthpost("MenaQ7")
search_healthpost("Solgar L-Theanine")
search_healthpost("Solgar NAC")
