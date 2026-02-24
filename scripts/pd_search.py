import urllib.request
import urllib.parse
import json

def search_pd(query):
    # Pharmacy Direct search
    url = f"https://www.pharmacydirect.co.nz/search.php?search_query={urllib.parse.quote(query)}"
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    )
    
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        links = []
        for line in html.split('\n'):
            if 'href="https://www.pharmacydirect.co.nz/' in line and '.html' in line and 'product' in line.lower():
                try:
                    start = line.index('href="') + 6
                    end = line.index('"', start)
                    link = line[start:end]
                    if link not in links:
                        links.append(link)
                except:
                    pass
        print(f"Results for '{query}':")
        for l in links[:3]:
            print(f"- {l}")
    except Exception as e:
        print(f"Error scraping Pharmacy Direct: {e}")

search_pd("Doctor's Best Vitamin K2")
search_pd("Solgar L-Theanine")
search_pd("Solgar NAC")
