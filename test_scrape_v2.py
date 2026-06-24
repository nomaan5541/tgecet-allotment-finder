"""
Test v2 - Debug the 500 error by trying different approaches.
"""

import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

BASE_URL = "https://tgecet.nic.in/college_allotment.aspx"
HOME_URL = "https://tgecet.nic.in/"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
})

# Step 1: Visit home page
print("Step 1: Visiting home page...")
r = session.get(HOME_URL, timeout=30)
print(f"  Status: {r.status_code}")
print(f"  Cookies: {dict(session.cookies)}")

time.sleep(1)

# Step 2: Visit allotment page
print("\nStep 2: Loading allotment page...")
r = session.get(BASE_URL, timeout=30)
print(f"  Status: {r.status_code}")
print(f"  Cookies: {dict(session.cookies)}")

soup = BeautifulSoup(r.text, 'lxml')

# Get ALL form fields
def get_all_fields(s):
    fields = {}
    for inp in s.find_all('input'):
        name = inp.get('name', '')
        if name:
            fields[name] = inp.get('value', '')
    return fields

all_fields = get_all_fields(soup)
print(f"\n  All form fields found:")
for k, v in all_fields.items():
    val_display = v[:50] + '...' if len(v) > 50 else v
    print(f"    {k} = {val_display}")

# Get college dropdown
college_dd = soup.find('select', {'id': 'MainContent_DropDownList1'})
print(f"\n  College dropdown name: {college_dd.get('name')}")

# Get branch dropdown
branch_dd = soup.find('select', {'id': 'MainContent_DropDownList2'})
print(f"  Branch dropdown name: {branch_dd.get('name')}")

# Check button
btn = soup.find('input', {'id': 'MainContent_btn_allot'})
if btn:
    print(f"  Button name: {btn.get('name')}")

# Check ScriptManager / UpdatePanel
sm = soup.find(attrs={'id': lambda x: x and 'ScriptManager' in str(x)})
if sm:
    print(f"\n  ScriptManager element found: {sm.get('id')}, name={sm.get('name')}")

# Check for ScriptManager hidden field
for inp in soup.find_all('input', {'type': 'hidden'}):
    name = inp.get('name', '')
    if 'script' in name.lower() or 'manager' in name.lower() or 'updatepanel' in name.lower():
        print(f"  ScriptManager/UpdatePanel field: {name}")

# Step 3: Try posting with proper headers (like a browser would)
print("\n\nStep 3: Trying POST with proper content-type and referer...")

form_data = {
    '__EVENTTARGET': 'SMPage$MainContent$DropDownList1',
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    '__VIEWSTATE': all_fields.get('__VIEWSTATE', ''),
    '__VIEWSTATEGENERATOR': all_fields.get('__VIEWSTATEGENERATOR', ''),
    '__EVENTVALIDATION': all_fields.get('__EVENTVALIDATION', ''),
    'SMPage$MainContent$DropDownList1': 'AARM',
    'SMPage$MainContent$DropDownList2': '0',
}

# Standard form POST headers
post_headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': BASE_URL,
    'Origin': 'https://tgecet.nic.in',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}

r = session.post(BASE_URL, data=form_data, headers=post_headers, timeout=30)
print(f"  Status: {r.status_code}")
print(f"  Response length: {len(r.text)}")

if r.status_code == 200:
    soup2 = BeautifulSoup(r.text, 'lxml')
    branch_dd2 = soup2.find('select', {'id': 'MainContent_DropDownList2'})
    if branch_dd2:
        opts = branch_dd2.find_all('option')
        print(f"  Branch dropdown has {len(opts)} options:")
        for opt in opts[:10]:
            print(f"    {opt['value']}: {opt.text.strip()}")
    else:
        print("  Branch dropdown not found in response!")
        # Check if the page has any error message
        error_div = soup2.find(class_='error') or soup2.find(id=lambda x: x and 'error' in str(x).lower())
        if error_div:
            print(f"  Error: {error_div.text.strip()[:200]}")
        # Print page title
        title = soup2.find('title')
        if title:
            print(f"  Page title: {title.text.strip()}")
        # Print first 500 chars of body
        body = soup2.find('body')
        if body:
            print(f"  Body preview: {body.text.strip()[:300]}")
else:
    print(f"  Response preview: {r.text[:500]}")

# Step 4: Try with different approach - form-encoded data manually
print("\n\nStep 4: Trying with URL-encoded data manually...")

# Build the exact same request a browser would make
manual_data = urllib.parse.urlencode({
    '__EVENTTARGET': 'SMPage$MainContent$DropDownList1',
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    '__VIEWSTATE': all_fields.get('__VIEWSTATE', ''),
    '__VIEWSTATEGENERATOR': all_fields.get('__VIEWSTATEGENERATOR', ''),
    '__EVENTVALIDATION': all_fields.get('__EVENTVALIDATION', ''),
    'SMPage$MainContent$DropDownList1': 'AARM',
    'SMPage$MainContent$DropDownList2': '0',
}, quote_via=urllib.parse.quote)

r = session.post(BASE_URL, data=manual_data.encode('utf-8'), headers=post_headers, timeout=30)
print(f"  Status: {r.status_code}")
print(f"  Response length: {len(r.text)}")

if r.status_code == 200:
    soup3 = BeautifulSoup(r.text, 'lxml')
    branch_dd3 = soup3.find('select', {'id': 'MainContent_DropDownList2'})
    if branch_dd3:
        opts = branch_dd3.find_all('option')
        print(f"  Branch dropdown has {len(opts)} options:")
        for opt in opts[:10]:
            print(f"    {opt['value']}: {opt.text.strip()}")
    else:
        print("  Branch dropdown not found!")
        title = soup3.find('title')
        if title:
            print(f"  Page title: {title.text.strip()}")

print("\n\nDone!")
