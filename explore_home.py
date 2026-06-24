from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(60)

# Step 1: Load home page and find all links
print('Loading home page...')
driver.get('https://tgecet.nic.in/')
time.sleep(3)
print('Title:', driver.title)

# Get all links on the page
links = driver.find_elements(By.TAG_NAME, 'a')
print('\nAll links on home page:')
for link in links:
    href = link.get_attribute('href') or ''
    text = link.text.strip()
    onclick = link.get_attribute('onclick') or ''
    if href or text or onclick:
        print('  text="%s" href="%s" onclick="%s"' % (text[:50], href[:80], onclick[:80]))

# Get all forms
forms = driver.find_elements(By.TAG_NAME, 'form')
print('\nForms:', len(forms))
for f in forms:
    print('  action=%s method=%s' % (f.get_attribute('action'), f.get_attribute('method')))

# Get page source to look for allotment link
src = driver.page_source
print('\nPage source length:', len(src))

# Search for allotment-related content
for keyword in ['allotment', 'allot', 'college_allotment', 'lnk', 'menu']:
    idx = src.lower().find(keyword)
    if idx >= 0:
        print('\nFound "%s" at position %d:' % (keyword, idx))
        print('  ...', src[max(0,idx-50):idx+100], '...')

# Also try clicking through frames if any
frames = driver.find_elements(By.TAG_NAME, 'iframe')
print('\nIframes:', len(frames))
for f in frames:
    print('  src=%s id=%s' % (f.get_attribute('src'), f.get_attribute('id')))

# Try the Default.aspx page
print('\n\nTrying Default.aspx...')
driver.get('https://tgecet.nic.in/Default.aspx')
time.sleep(3)
print('Title:', driver.title)
links2 = driver.find_elements(By.TAG_NAME, 'a')
for link in links2:
    href = link.get_attribute('href') or ''
    text = link.text.strip()
    if 'allot' in href.lower() or 'allot' in text.lower() or 'college' in text.lower():
        print('  MATCH: text="%s" href="%s"' % (text[:50], href[:80]))

driver.quit()
