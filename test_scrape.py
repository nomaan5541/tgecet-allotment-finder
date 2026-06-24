"""
Quick test of the scraper - just tries 2 colleges to verify the approach works.
"""

import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://tgecet.nic.in/college_allotment.aspx"
HOME_URL = "https://tgecet.nic.in/"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': HOME_URL,
})

# Step 1: Visit home page
print("Step 1: Visiting home page...")
r = session.get(HOME_URL, timeout=30)
print(f"  Home page status: {r.status_code}")

time.sleep(1)

# Step 2: Visit allotment page
print("\nStep 2: Loading allotment page...")
r = session.get(BASE_URL, timeout=30)
print(f"  Allotment page status: {r.status_code}")

soup = BeautifulSoup(r.text, 'lxml')

# Get ASP.NET fields
def get_fields(s):
    fields = {}
    for name in ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
                 '__EVENTTARGET', '__EVENTARGUMENT', '__LASTFOCUS']:
        el = s.find('input', {'name': name})
        if el:
            fields[name] = el.get('value', '')
    return fields

asp = get_fields(soup)

# Check college dropdown
college_dd = soup.find('select', {'id': 'MainContent_DropDownList1'})
if college_dd:
    options = college_dd.find_all('option')
    print(f"\n  Found college dropdown with {len(options)} options")
    # Show first 3
    for opt in options[:5]:
        print(f"    {opt['value']}: {opt.text.strip()}")
else:
    print("  ERROR: Could not find college dropdown!")
    # Debug: find all selects
    selects = soup.find_all('select')
    print(f"  Found {len(selects)} select elements:")
    for s in selects:
        print(f"    id={s.get('id')}, name={s.get('name')}")
    import sys
    sys.exit(1)

# Step 3: Select first college (AARM)
print("\nStep 3: Selecting first college (AARM)...")
form_data = {
    '__EVENTTARGET': 'SMPage$MainContent$DropDownList1',
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    '__VIEWSTATE': asp['__VIEWSTATE'],
    '__VIEWSTATEGENERATOR': asp.get('__VIEWSTATEGENERATOR', ''),
    '__EVENTVALIDATION': asp.get('__EVENTVALIDATION', ''),
    'SMPage$MainContent$DropDownList1': 'AARM',
    'SMPage$MainContent$DropDownList2': '0',
}

r = session.post(BASE_URL, data=form_data, timeout=30)
print(f"  Post status: {r.status_code}")

soup = BeautifulSoup(r.text, 'lxml')
asp = get_fields(soup)

# Check branches
branch_dd = soup.find('select', {'id': 'MainContent_DropDownList2'})
if branch_dd:
    options = branch_dd.find_all('option')
    print(f"\n  Branch dropdown has {len(options)} options:")
    branches = []
    for opt in options:
        val = opt['value']
        txt = opt.text.strip()
        print(f"    {val}: {txt}")
        if val and val != '0':
            branches.append(val)
else:
    print("  ERROR: No branch dropdown found!")
    import sys
    sys.exit(1)

# Step 4: Submit for first branch
if branches:
    first_branch = branches[0]
    print(f"\nStep 4: Getting allotments for AARM - {first_branch}...")
    
    form_data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': asp['__VIEWSTATE'],
        '__VIEWSTATEGENERATOR': asp.get('__VIEWSTATEGENERATOR', ''),
        '__EVENTVALIDATION': asp.get('__EVENTVALIDATION', ''),
        'SMPage$MainContent$DropDownList1': 'AARM',
        'SMPage$MainContent$DropDownList2': first_branch,
        'SMPage$MainContent$btn_allot': 'Show Allotments',
    }
    
    r = session.post(BASE_URL, data=form_data, timeout=30)
    print(f"  Post status: {r.status_code}")
    
    soup = BeautifulSoup(r.text, 'lxml')
    
    # Find the results table
    table = soup.find('table', class_='sortable')
    if table:
        rows = table.find_all('tr')
        print(f"\n  Found table with {len(rows)} rows (including header)")
        
        # Print header
        header = rows[0]
        ths = header.find_all('th')
        if ths:
            print(f"  Headers: {[th.text.strip() for th in ths]}")
        
        # Print first 5 data rows
        print("\n  First 5 students:")
        for row in rows[1:6]:
            cells = row.find_all('td')
            data = [c.text.strip() for c in cells]
            print(f"    {data}")
    else:
        # Check for any table
        tables = soup.find_all('table')
        print(f"\n  No 'sortable' table found. Total tables on page: {len(tables)}")
        for i, t in enumerate(tables):
            cls = t.get('class', [])
            tid = t.get('id', '')
            rows_count = len(t.find_all('tr'))
            print(f"    Table {i}: class={cls}, id={tid}, rows={rows_count}")
        
        # Try looking for GridView
        gridview = soup.find('table', {'id': lambda x: x and 'GridView' in x})
        if gridview:
            rows = gridview.find_all('tr')
            print(f"\n  Found GridView table with {len(rows)} rows")
            for row in rows[:3]:
                cells = row.find_all(['th', 'td'])
                print(f"    {[c.text.strip() for c in cells]}")

print("\n\nTest complete!")
