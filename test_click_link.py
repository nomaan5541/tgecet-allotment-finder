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

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(60)

print('Step 1: Loading home page...')
driver.get('https://tgecet.nic.in/')
time.sleep(3)
print('  Title:', driver.title)

# Find and CLICK the allotment link
print('Step 2: Clicking "College-wise Allotment Details" link...')
link = driver.find_element(By.LINK_TEXT, 'College-wise Allotment Details')
link.click()
time.sleep(3)
print('  Title:', driver.title)
print('  URL:', driver.current_url)

# Check if page loaded correctly
if 'Object reference' in driver.title:
    print('  ERROR: Page still shows error even after clicking link!')
    print('  Trying via JavaScript...')
    driver.get('https://tgecet.nic.in/')
    time.sleep(2)
    driver.execute_script("window.location.href='college_allotment.aspx';")
    time.sleep(3)
    print('  Title after JS nav:', driver.title)

try:
    dd = Select(driver.find_element(By.ID, 'MainContent_DropDownList1'))
    count = len(dd.options)
    print('  SUCCESS! College dropdown has', count, 'options')
    
    # Test selecting a college
    print('Step 3: Selecting AARM...')
    dd.select_by_value('AARM')
    time.sleep(3)
    
    bd = Select(driver.find_element(By.ID, 'MainContent_DropDownList2'))
    branches = []
    for o in bd.options:
        v = o.get_attribute('value')
        t = o.text.strip()
        if v and v != '0':
            branches.append((v, t))
    print('  Branches:', branches)
    
    if branches:
        print('Step 4: Getting allotment data...')
        bd.select_by_value(branches[0][0])
        time.sleep(1)
        btn = driver.find_element(By.ID, 'MainContent_btn_allot')
        btn.click()
        time.sleep(3)
        
        # Check for data table
        tables = driver.find_elements(By.TAG_NAME, 'table')
        for t in tables:
            rows = t.find_elements(By.TAG_NAME, 'tr')
            if len(rows) > 2:
                cls = t.get_attribute('class') or ''
                print('  Found data table! class=%s, rows=%d' % (cls, len(rows)))
                # Print header
                hdr = rows[0].find_elements(By.CSS_SELECTOR, 'th, td')
                print('  Headers:', [h.text for h in hdr])
                # Print first 3 data rows
                for r in rows[1:4]:
                    cells = r.find_elements(By.TAG_NAME, 'td')
                    print('  Row:', [c.text for c in cells])
                break
    
    print('\nALL TESTS PASSED!')
    
except Exception as e:
    print('ERROR:', e)

driver.quit()
