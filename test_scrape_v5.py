"""
Test v5 - With retry logic to handle intermittent 500 errors.
"""

import requests
from bs4 import BeautifulSoup
import time

HOME_URL = "https://tgecet.nic.in/"
BASE_URL = "https://tgecet.nic.in/college_allotment.aspx"

def make_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Upgrade-Insecure-Requests': '1',
    })
    return session

def get_with_retry(session, url, max_retries=5, delay=3):
    """GET with retries for intermittent 500 errors."""
    for attempt in range(max_retries):
        try:
            r = session.get(url, timeout=30)
            if r.status_code == 200:
                return r
            print(f"  Attempt {attempt+1}: status {r.status_code}, retrying in {delay}s...")
        except Exception as e:
            print(f"  Attempt {attempt+1}: error {e}, retrying in {delay}s...")
        time.sleep(delay)
        # On repeated failures, create a fresh session
        if attempt >= 2:
            session = make_session()
    return None

def post_with_retry(session, url, data, max_retries=3, delay=3):
    """POST with retries."""
    for attempt in range(max_retries):
        try:
            r = session.post(url, data=data, headers={
                'Referer': BASE_URL,
                'Origin': 'https://tgecet.nic.in',
                'Content-Type': 'application/x-www-form-urlencoded',
            }, timeout=30)
            if r.status_code == 200:
                return r
            print(f"  POST attempt {attempt+1}: status {r.status_code}, retrying...")
        except Exception as e:
            print(f"  POST attempt {attempt+1}: error {e}, retrying...")
        time.sleep(delay)
    return None

def get_fields(soup):
    fields = {}
    for inp in soup.find_all('input', {'type': 'hidden'}):
        name = inp.get('name', '')
        if name:
            fields[name] = inp.get('value', '')
    return fields

# Step 1: Load page with retries
session = make_session()
print("Loading allotment page (with retries)...")
r = get_with_retry(session, BASE_URL)
if not r:
    print("FATAL: Could not load the allotment page after retries!")
    exit(1)

print(f"  Status: {r.status_code}, Length: {len(r.text)}")
soup = BeautifulSoup(r.text, 'lxml')
asp = get_fields(soup)

college_dd = soup.find('select', {'id': 'MainContent_DropDownList1'})
if not college_dd:
    print("FATAL: College dropdown not found!")
    exit(1)

colleges = []
for opt in college_dd.find_all('option'):
    v = opt.get('value', '')
    if v and v != '0':
        colleges.append((v, opt.text.strip()))

print(f"  Found {len(colleges)} colleges")

# Step 2: Select first college  
code, name = colleges[0]
print(f"\nSelecting college: {code} - {name}")

post_data = dict(asp)
post_data.update({
    '__EVENTTARGET': 'SMPage$MainContent$DropDownList1',
    '__EVENTARGUMENT': '',
    'SMPage$MainContent$DropDownList1': code,
    'SMPage$MainContent$DropDownList2': '0',
})

r = post_with_retry(session, BASE_URL, post_data)
if not r:
    print("FATAL: POST failed after retries!")
    # Try fresh session
    print("Trying fresh session...")
    session = make_session()
    r = get_with_retry(session, BASE_URL)
    if r:
        soup = BeautifulSoup(r.text, 'lxml')
        asp = get_fields(soup)
        post_data = dict(asp)
        post_data.update({
            '__EVENTTARGET': 'SMPage$MainContent$DropDownList1',
            '__EVENTARGUMENT': '',
            'SMPage$MainContent$DropDownList1': code,
            'SMPage$MainContent$DropDownList2': '0',
        })
        r = post_with_retry(session, BASE_URL, post_data)
    
    if not r:
        print("FATAL: Could not POST even with fresh session!")
        exit(1)

soup2 = BeautifulSoup(r.text, 'lxml')
asp2 = get_fields(soup2)

branch_dd = soup2.find('select', {'id': 'MainContent_DropDownList2'})
if branch_dd:
    branches = []
    for opt in branch_dd.find_all('option'):
        v = opt.get('value', '')
        t = opt.text.strip()
        if v and v != '0':
            branches.append((v, t))
        print(f"    Branch option: value='{v}', text='{t}'")
    
    print(f"\n  Found {len(branches)} branches")
    
    if branches:
        bcode, bname = branches[0]
        print(f"\nGetting data for branch: {bcode} - {bname}")
        
        post_data2 = dict(asp2)
        post_data2.update({
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            'SMPage$MainContent$DropDownList1': code,
            'SMPage$MainContent$DropDownList2': bcode,
            'SMPage$MainContent$btn_allot': 'Show Allotments',
        })
        
        r2 = post_with_retry(session, BASE_URL, post_data2)
        
        if r2:
            soup3 = BeautifulSoup(r2.text, 'lxml')
            
            # Try to find any table with data
            all_tables = soup3.find_all('table')
            print(f"  Found {len(all_tables)} tables total")
            
            for i, t in enumerate(all_tables):
                rows = t.find_all('tr')
                if len(rows) > 1:
                    print(f"\n  Table {i} (class={t.get('class')}, id={t.get('id')}) - {len(rows)} rows")
                    # Print header
                    first_row = rows[0]
                    cells = first_row.find_all(['th', 'td'])
                    if cells:
                        print(f"    Header: {[c.text.strip() for c in cells]}")
                    # Print first data row
                    if len(rows) > 1:
                        cells2 = rows[1].find_all('td')
                        if cells2:
                            print(f"    Row 1: {[c.text.strip() for c in cells2]}")
                    if len(rows) > 2:
                        cells3 = rows[2].find_all('td')
                        if cells3:
                            print(f"    Row 2: {[c.text.strip() for c in cells3]}")
        else:
            print("  Failed to get data!")
else:
    print("  Branch dropdown not found!")
    # Debug
    selects = soup2.find_all('select')
    print(f"  Selects found: {len(selects)}")
    for s in selects:
        print(f"    id={s.get('id')}, name={s.get('name')}, options={len(s.find_all('option'))}")

print("\nDone!")
