"""
Test v4 - Full test of select college -> get branches -> get data flow.
"""

import requests
from bs4 import BeautifulSoup
import time

HOME_URL = "https://tgecet.nic.in/"
BASE_URL = "https://tgecet.nic.in/college_allotment.aspx"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Upgrade-Insecure-Requests': '1',
})

def get_fields(soup):
    fields = {}
    for inp in soup.find_all('input', {'type': 'hidden'}):
        name = inp.get('name', '')
        if name:
            fields[name] = inp.get('value', '')
    return fields

# Step 1: Load allotment page
print("Loading allotment page...")
r = session.get(BASE_URL, timeout=30)
print(f"  Status: {r.status_code}, Length: {len(r.text)}")
print(f"  Cookies: {dict(session.cookies)}")

soup = BeautifulSoup(r.text, 'lxml')
asp = get_fields(soup)
print(f"  Hidden fields: {list(asp.keys())}")

# Get first 3 college codes
college_dd = soup.find('select', {'id': 'MainContent_DropDownList1'})
colleges = []
for opt in college_dd.find_all('option'):
    v = opt.get('value', '')
    if v and v != '0':
        colleges.append((v, opt.text.strip()))

print(f"  Colleges: {len(colleges)}")

# Step 2: Select first college
code, name = colleges[0]
print(f"\nSelecting college: {code} - {name}")

post_data = dict(asp)  # Start with all hidden fields
post_data.update({
    '__EVENTTARGET': 'SMPage$MainContent$DropDownList1',
    '__EVENTARGUMENT': '',
    'SMPage$MainContent$DropDownList1': code,
    'SMPage$MainContent$DropDownList2': '0',
})

r = session.post(BASE_URL, data=post_data, headers={
    'Referer': BASE_URL,
    'Origin': 'https://tgecet.nic.in',
    'Content-Type': 'application/x-www-form-urlencoded',
}, timeout=30)
print(f"  Status: {r.status_code}, Length: {len(r.text)}")

if r.status_code != 200:
    print(f"  Error body: {r.text[:500]}")
else:
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
            print(f"    Option: value='{v}', text='{t}'")
        
        print(f"\n  Found {len(branches)} branches")
        
        if branches:
            # Step 3: Get data for first branch
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
            
            r2 = session.post(BASE_URL, data=post_data2, headers={
                'Referer': BASE_URL,
                'Origin': 'https://tgecet.nic.in',
                'Content-Type': 'application/x-www-form-urlencoded',
            }, timeout=30)
            print(f"  Status: {r2.status_code}, Length: {len(r2.text)}")
            
            if r2.status_code == 200:
                soup3 = BeautifulSoup(r2.text, 'lxml')
                
                # Find ALL tables
                tables = soup3.find_all('table')
                print(f"  Found {len(tables)} tables")
                
                for i, t in enumerate(tables):
                    rows = t.find_all('tr')
                    cls = t.get('class', [])
                    tid = t.get('id', '')
                    print(f"    Table {i}: class={cls}, id={tid}, rows={len(rows)}")
                
                # Look for sortable table
                data_table = soup3.find('table', class_='sortable')
                if not data_table:
                    # Try to find by GridView
                    data_table = soup3.find('table', {'id': lambda x: x and 'GridView' in str(x)})
                
                if data_table:
                    rows = data_table.find_all('tr')
                    print(f"\n  Data table has {len(rows)} rows")
                    
                    # Header
                    header = rows[0]
                    ths = header.find_all(['th', 'td'])
                    print(f"  Headers: {[h.text.strip() for h in ths]}")
                    
                    # First 3 data rows
                    for row in rows[1:4]:
                        cells = row.find_all('td')
                        print(f"  Data: {[c.text.strip() for c in cells]}")
                else:
                    print("\n  No data table found!")
                    # Print some text from the page
                    body_text = soup3.get_text()
                    # Look for "no records" or similar
                    for line in body_text.split('\n'):
                        line = line.strip()
                        if line and len(line) > 5 and len(line) < 200:
                            if any(w in line.lower() for w in ['record', 'allot', 'no data', 'result']):
                                print(f"    Found: {line}")
    else:
        print("  Branch dropdown not found!")
        title = soup2.find('title')
        print(f"  Page title: {title.text.strip() if title else 'N/A'}")

print("\nDone!")
