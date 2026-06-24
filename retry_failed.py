"""
Retry scraping the failed college-branch combinations.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
import json
import time
import os

BASE_URL = "https://tgecet.nic.in/college_allotment.aspx"
PROGRESS_FILE = r"d:\COLLAGE BROS\scrape_progress.json"

FAILED_COMBOS = [
    ('AKIT', 'EEE'), ('AKIT', 'ECE'), ('AKIT', 'MEC'), ('AKIT', 'MIN'),
    ('ASRA', 'CSD'), ('ASRA', 'EEE'), ('ASRA', 'ECE'), ('ASRA', 'MEC'),
    ('AVIH', 'EEE'), ('AVIH', 'ECE'), ('AVIH', 'MEC'),
    ('BOMA', 'CSM'), ('BOMA', 'EEE'), ('BOMA', 'ECE'),
    ('BOSE', 'EEE'), ('BOSE', 'ECE'),
    ('BRIG', 'PHM'), ('BRIG', 'CIV'), ('BRIG', 'CSB'), ('BRIG', 'CSE'),
    ('BRIG', 'CSM'), ('BRIG', 'CSD'), ('BRIG', 'EEE'), ('BRIG', 'ECE'), ('BRIG', 'MEC'),
    ('BRIL', 'EEE'), ('BRIL', 'ECE'), ('BRIL', 'MEC'),
    ('CHTN', 'CSE'), ('CHTN', 'EEE'), ('CHTN', 'ECE'), ('CHTN', 'MEC'),
    ('DARE', 'ECE'), ('DCET', 'MEC'),
    ('DRKI', 'CSD'), ('DRKI', 'EEE'), ('DRKI', 'ECE'), ('DRKI', 'MEC'),
    ('GATE', 'CIV'), ('GATE', 'CSE'), ('GATE', 'EEE'), ('GATE', 'ECE'), ('GATE', 'MEC'), ('GATE', 'MIN'),
    ('GKEM', 'INF'),
    ('GLOB', 'CSD'), ('GLOB', 'ECE'), ('GLOB', 'MEC'),
    ('GURU', 'CIV'), ('GURU', 'CSE'), ('GURU', 'CSM'), ('GURU', 'CSC'), ('GURU', 'CSD'),
    ('GURU', 'CSO'), ('GURU', 'EEE'), ('GURU', 'ECE'), ('GURU', 'EVL'), ('GURU', 'INF'), ('GURU', 'MEC'),
    ('HOLY', 'CSD'), ('HOLY', 'CSO'), ('HOLY', 'EEE'), ('HOLY', 'ECE'), ('HOLY', 'MEC'),
    ('INDI', 'ECE'),
    ('INDU', 'EEE'), ('INDU', 'ECE'), ('INDU', 'INF'), ('INDU', 'MEC'),
    ('JBIT', 'INF'), ('JBIT', 'MEC'),
    ('JMTS', 'EEE'), ('JMTS', 'ECE'),
    ('JOGI', 'EEE'), ('JOGI', 'ECE'), ('JOGI', 'INF'), ('JOGI', 'MEC'),
    ('KLRT', 'EEE'), ('KLRT', 'ECE'), ('KLRT', 'MEC'), ('KLRT', 'MIN'),
    ('KNRR', 'EEE'), ('KNRR', 'ECE'), ('KNRR', 'MEC'),
    ('KTKM', 'MEC'),
    ('MDRK', 'CSM'), ('MDRK', 'EEE'), ('MDRK', 'ECE'), ('MDRK', 'MEC'),
    ('MGHA', 'EEE'), ('MGHA', 'ECE'),
    ('MINA', 'CSM'), ('MINA', 'CSD'), ('MINA', 'EEE'), ('MINA', 'ECE'),
    ('MMTZ', 'CIC'),
    ('NNRG', 'CIV'), ('NNRG', 'CSE'), ('NNRG', 'CSM'), ('NNRG', 'CSD'), ('NNRG', 'ECE'),
    ('PALV', 'EEE'), ('PALV', 'ECE'),
    ('PRIW', 'CSE'), ('PRIW', 'CSM'), ('PRIW', 'ECE'),
    ('SANA', 'CSM'), ('SANA', 'CSC'), ('SANA', 'CSD'), ('SANA', 'EEE'), ('SANA', 'ECE'),
    ('SBIT', 'EEE'), ('SBIT', 'ECE'),
    ('SCET', 'AIM'), ('SCET', 'CIV'), ('SCET', 'CSE'), ('SCET', 'CSM'), ('SCET', 'CSD'),
    ('SCET', 'EEE'), ('SCET', 'ECE'), ('SCET', 'INF'), ('SCET', 'MEC'),
    ('SDES', 'CSI'), ('SDES', 'EEE'), ('SDES', 'ECE'), ('SDES', 'MEC'),
    ('SDGI', 'CSD'), ('SDGI', 'EEE'), ('SDGI', 'ECE'),
    ('SISG', 'CSE'), ('SISG', 'CSM'), ('SISG', 'CSC'), ('SISG', 'CSD'),
    ('SISG', 'CSO'), ('SISG', 'EEE'), ('SISG', 'ECE'), ('SISG', 'MEC'),
    ('SMCD', 'CSE'), ('SMCD', 'CSM'),
    ('SMED', 'PHM'), ('SMED', 'CSE'), ('SMED', 'CSM'),
    ('SMSK', 'EEE'), ('SMSK', 'ECE'),
    ('SPHN', 'ECE'),
    ('STLW', 'CSE'), ('STLW', 'CSM'), ('STLW', 'EEE'), ('STLW', 'ECE'), ('STLW', 'INF'),
    ('SWET', 'CSE'), ('SWET', 'CSM'), ('SWET', 'CSD'), ('SWET', 'ECE'), ('SWET', 'INF'),
    ('TCTK', 'EEE'), ('TCTK', 'ECE'),
    ('TPCE', 'ECE'),
    ('VGNT', 'MEC'),
    ('VISA', 'CSD'), ('VISA', 'ECE'), ('VISA', 'INF'), ('VISA', 'MEC'),
    ('VITS', 'EEE'), ('VITS', 'ECE'),
    ('VJYA', 'CSD'), ('VJYA', 'EEE'), ('VJYA', 'ECE'),
    ('VRKW', 'CSE'), ('VRKW', 'CSM'), ('VRKW', 'CSD'), ('VRKW', 'EEE'), ('VRKW', 'ECE'),
]


def setup_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(5)
    return driver


def navigate_to_allotment(driver):
    driver.get("https://tgecet.nic.in/default.aspx")
    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(2)
    driver.execute_script("window.open('https://tgecet.nic.in/college_allotment.aspx', '_self')")
    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(1)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "MainContent_DropDownList1")))


def scrape_combo(driver, college_code, branch_code):
    """Scrape a single college-branch combination."""
    # Select college
    dd = Select(driver.find_element(By.ID, 'MainContent_DropDownList1'))
    dd.select_by_value(college_code)
    WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(1)

    # Get college name
    dd2 = Select(driver.find_element(By.ID, 'MainContent_DropDownList1'))
    college_name = dd2.first_selected_option.text.strip()

    # Select branch
    bd = Select(driver.find_element(By.ID, 'MainContent_DropDownList2'))
    try:
        bd.select_by_value(branch_code)
    except:
        return [], college_name, "Branch not found"
    
    branch_name = None
    for o in bd.options:
        if o.get_attribute('value') == branch_code:
            branch_name = o.text.strip()
            break
    
    time.sleep(0.5)
    btn = driver.find_element(By.ID, 'MainContent_btn_allot')
    btn.click()
    WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(1)

    # Scrape table
    students = []
    tables = driver.find_elements(By.TAG_NAME, 'table')
    for t in tables:
        cls = t.get_attribute('class') or ''
        if 'sortable' in cls:
            rows = t.find_elements(By.TAG_NAME, 'tr')
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) >= 8:
                    students.append({
                        'college_code': college_code,
                        'college_name': college_name,
                        'branch_code': branch_code,
                        'branch_name': branch_name or branch_code,
                        'S.No': cells[0].text.strip(),
                        'Hall Ticket No': cells[1].text.strip(),
                        'Rank': cells[2].text.strip(),
                        'Name': cells[3].text.strip(),
                        'Sex': cells[4].text.strip(),
                        'Caste': cells[5].text.strip(),
                        'Region': cells[6].text.strip(),
                        'Seat Category': cells[7].text.strip(),
                    })
            break
    
    return students, college_name, None


def main():
    print(f"Retrying {len(FAILED_COMBOS)} failed combinations...")
    
    # Load existing progress
    with open(PROGRESS_FILE, 'r') as f:
        progress = json.load(f)
    
    existing_data = progress['all_data']
    print(f"Existing records: {len(existing_data)}")
    
    driver = setup_driver()
    new_records = []
    still_failed = []
    
    try:
        navigate_to_allotment(driver)
        print("Page loaded!\n")
        
        # Group by college to minimize page reloads
        from collections import defaultdict
        college_groups = defaultdict(list)
        for cc, bc in FAILED_COMBOS:
            college_groups[cc].append(bc)
        
        total = len(FAILED_COMBOS)
        done = 0
        
        for cc, branches in college_groups.items():
            for bc in branches:
                done += 1
                try:
                    students, cn, err = scrape_combo(driver, cc, bc)
                    if err:
                        print(f"  [{done}/{total}] {cc}/{bc}: {err}")
                        still_failed.append((cc, bc))
                    else:
                        new_records.extend(students)
                        print(f"  [{done}/{total}] {cc}/{bc}: {len(students)} students")
                    time.sleep(0.3)
                except Exception as e:
                    print(f"  [{done}/{total}] {cc}/{bc}: ERROR - {str(e)[:80]}")
                    still_failed.append((cc, bc))
                    try:
                        navigate_to_allotment(driver)
                    except:
                        try:
                            driver.quit()
                            driver = setup_driver()
                            navigate_to_allotment(driver)
                        except:
                            pass
                    time.sleep(1)
        
        # Merge data
        all_data = existing_data + new_records
        
        # Save updated progress
        with open(PROGRESS_FILE, 'w') as f:
            json.dump({'completed_colleges': progress['completed_colleges'], 'all_data': all_data}, f)
        
        print(f"\n{'='*50}")
        print(f"  Retry complete!")
        print(f"  New records: {len(new_records)}")
        print(f"  Total records: {len(all_data)}")
        print(f"  Still failed: {len(still_failed)}")
        print(f"{'='*50}")
        
        if still_failed:
            print("\nStill failed:")
            for sf in still_failed:
                print(f"  {sf}")
    
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
