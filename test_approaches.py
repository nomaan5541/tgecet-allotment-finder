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

# Try multiple approaches to get to the allotment page

# Approach 1: Direct with session cookie manipulation
print('=== Approach 1: Set cookie then navigate ===')
driver.get('https://tgecet.nic.in/')
time.sleep(2)
cookies = driver.get_cookies()
print('Cookies after home:', cookies)

# Navigate to allotment using JavaScript
driver.execute_script("window.open('https://tgecet.nic.in/college_allotment.aspx', '_self')")
time.sleep(3)
print('Title:', driver.title)

if 'Object reference' in driver.title:
    print('Still error. Trying approach 2...')
    
    # Approach 2: Use the link href directly
    print('\n=== Approach 2: Navigate using location.assign ===')
    driver.get('https://tgecet.nic.in/')
    time.sleep(2)
    driver.execute_script("document.location.assign('college_allotment.aspx')")
    time.sleep(3)
    print('Title:', driver.title)
    print('URL:', driver.current_url)

if 'Object reference' in driver.title:
    print('Still error. Trying approach 3...')
    
    # Approach 3: Click the link via JS
    print('\n=== Approach 3: Click link via JS ===')
    driver.get('https://tgecet.nic.in/')
    time.sleep(2)
    links = driver.find_elements(By.TAG_NAME, 'a')
    for link in links:
        href = link.get_attribute('href') or ''
        if 'college_allotment' in href:
            print('Found link:', href)
            # Try clicking via JS
            driver.execute_script("arguments[0].click()", link)
            time.sleep(3)
            print('Title after click:', driver.title)
            print('URL:', driver.current_url)
            break

if 'Object reference' in driver.title:
    print('Still error. Trying approach 4...')
    
    # Approach 4: Use the qAPIfeeOnline page or cand_login to see if session is needed
    print('\n=== Approach 4: Try with POST ===')
    driver.get('https://tgecet.nic.in/')
    time.sleep(2)
    # Get current page source for session info
    src = driver.page_source
    # Look for session/viewstate info
    import re
    vs_match = re.search(r'__VIEWSTATE.*?value="(.*?)"', src)
    if vs_match:
        print('Found ViewState (length):', len(vs_match.group(1)))
    
    # Approach 5: Try with cookies set explicitly
    print('\n=== Approach 5: Multiple page loads ===')
    for i in range(3):
        driver.get('https://tgecet.nic.in/college_allotment.aspx')
        time.sleep(2)
        print(f'  Attempt {i+1}: Title: {driver.title}')
        if 'Object reference' not in driver.title:
            break

# Final check
print('\n\nFinal check - current page:')
print('Title:', driver.title)
print('URL:', driver.current_url)

try:
    dd = driver.find_element(By.ID, 'MainContent_DropDownList1')
    print('SUCCESS! Found dropdown!')
except:
    print('FAILED - dropdown not found')
    
    # Debug: Let's check what the error page says
    print('\nError page content:')
    body = driver.find_element(By.TAG_NAME, 'body')
    print(body.text[:1000])

driver.quit()
