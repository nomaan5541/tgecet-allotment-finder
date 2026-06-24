from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(60)

print('Step 1: Loading home page...')
driver.get('https://tgecet.nic.in/default.aspx')
time.sleep(3)
print('  Title:', driver.title)

print('Step 2: Loading allotment page...')
driver.get('https://tgecet.nic.in/college_allotment.aspx')
time.sleep(3)
print('  Title:', driver.title)

try:
    dd = Select(driver.find_element(By.ID, 'MainContent_DropDownList1'))
    print('  College dropdown:', len(dd.options), 'options')
    
    # Try selecting a college
    print('Step 3: Selecting AARM...')
    dd.select_by_value('AARM')
    time.sleep(3)
    
    # Get branches
    bd = Select(driver.find_element(By.ID, 'MainContent_DropDownList2'))
    branches = []
    for o in bd.options:
        v = o.get_attribute('value')
        t = o.text.strip()
        if v and v != '0':
            branches.append((v, t))
    print('  Branches:', branches)
    
    if branches:
        # Select first branch and click show
        bd.select_by_value(branches[0][0])
        time.sleep(1)
        btn = driver.find_element(By.ID, 'MainContent_btn_allot')
        btn.click()
        time.sleep(3)
        
        # Find table
        tables = driver.find_elements(By.TAG_NAME, 'table')
        for t in tables:
            rows = t.find_elements(By.TAG_NAME, 'tr')
            if len(rows) > 2:
                cls = t.get_attribute('class') or ''
                tid = t.get_attribute('id') or ''
                print('  Table: class=%s, id=%s, rows=%d' % (cls, tid, len(rows)))
                # Print first data row
                if len(rows) > 1:
                    cells = rows[1].find_elements(By.TAG_NAME, 'td')
                    print('  First row:', [c.text for c in cells])
                break
    
    print('SUCCESS!')
except Exception as e:
    print('ERROR:', e)
    # Get page source for debugging
    print('Page title:', driver.title)
    print('Page source preview:', driver.page_source[:500])

driver.quit()
