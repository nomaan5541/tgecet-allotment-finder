"""
Test v3 - More careful session handling. The ASP.NET page might need 
cookies from the initial page load.
"""

import requests
from bs4 import BeautifulSoup
import time

HOME_URL = "https://tgecet.nic.in/"
BASE_URL = "https://tgecet.nic.in/college_allotment.aspx"

# Create session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Upgrade-Insecure-Requests': '1',
})

# Step 1: Visit home page
print("Step 1: Visiting home page...")
r = session.get(HOME_URL, timeout=30)
print(f"  Status: {r.status_code}")
print(f"  Cookies: {dict(session.cookies)}")
print(f"  Response headers: {dict(r.headers)}")

time.sleep(2)

# Step 2: Visit allotment page with proper headers
print("\nStep 2: Loading allotment page...")
session.headers.update({
    'Referer': HOME_URL,
    'Sec-Fetch-Site': 'same-origin',
})
r = session.get(BASE_URL, timeout=30, allow_redirects=True)
print(f"  Status: {r.status_code}")
print(f"  URL after redirect: {r.url}")
print(f"  Cookies: {dict(session.cookies)}")
print(f"  Response length: {len(r.text)}")
print(f"  Response headers: {dict(r.headers)}")

if r.status_code == 500:
    print(f"\n  500 ERROR - response body preview:")
    print(r.text[:1000])
elif r.status_code == 200:
    soup = BeautifulSoup(r.text, 'lxml')
    title = soup.find('title')
    if title:
        print(f"  Page title: {title.text.strip()}")
    
    # Find dropdowns
    selects = soup.find_all('select')
    print(f"  Found {len(selects)} select elements")
    for s in selects:
        opts = s.find_all('option')
        print(f"    name={s.get('name')}, id={s.get('id')}, options={len(opts)}")

# Step 3: Try direct URL with query parameters
print("\nStep 3: Trying other pages on the site...")
pages = [
    "https://tgecet.nic.in/Default.aspx",
    "https://tgecet.nic.in/",
    "https://tgecet.nic.in/college_allotment.aspx",
]
for url in pages:
    try:
        r2 = session.get(url, timeout=15)
        print(f"  {url} -> Status: {r2.status_code}")
    except Exception as e:
        print(f"  {url} -> Error: {e}")

print("\n\nDone!")
