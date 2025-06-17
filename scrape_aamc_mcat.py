import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

SELECTORS = {
    'next_button': "//a[@aria-label='Next' and contains(@class, 'next')]",
    'question_counter': "//h2[contains(@class, 'title')]",
    'passage': "//div[contains(@class, 'reading-passage')]",
    'question_text': "//div[contains(@id, 'current-question-container')]//p",
    'answer_choices': "//ul[contains(@class, 'question-choices-multi')]//li",
    'correct_answer': "//div[contains(@class, 'multi-choice correct')]/@data-choice",
    'solution': "//div[@id='answer']",
    'skills_tags': "//div[contains(@class, 'tag')]"
}

def navigate_next(driver):
    """Navigate to next question using arrow keys with focus management."""
    try:
        # Ensure browser window has focus
        driver.switch_to.window(driver.current_window_handle)
        
        # Focus on a reliable element and send arrow key
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()  # Ensure focus
        time.sleep(0.5)
        body.send_keys(Keys.ARROW_RIGHT)
        
        print("  → Arrow key sent")
        return True
    except Exception as e:
        print(f"  ❌ Arrow navigation failed: {e}")
        return False

def wait_for_page_change(driver, current_question_num, timeout=10):
    """Wait for question number to change."""
    target_question = current_question_num + 1
    
    for attempt in range(timeout * 2):
        time.sleep(0.5)
        try:
            title_selectors = [
                "//h2[contains(@class, 'title')]",
                "//*[contains(text(), 'Question')]"
            ]
            
            for selector in title_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    title_text = elem.text.strip()
                    if f"Question {target_question}" in title_text or f"{target_question} of" in title_text:
                        print(f"  ✅ Question {target_question} loaded")
                        return True
        except:
            continue
    
    print(f"  ⚠️ Timeout waiting for Question {target_question}")
    return False

def extract_data(driver, question_num):
    """Extract question data with enhanced error handling."""
    data = {'question_number': question_num}
    
    # Passage content
    try:
        passage_elem = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, SELECTORS['passage']))
        )
        data['passage'] = passage_elem.text.strip()
    except TimeoutException:
        data['passage'] = None
        print("    ⚠️ No passage found")
    
    # Question text
    try:
        question_elem = driver.find_element(By.XPATH, SELECTORS['question_text'])
        data['question_text'] = question_elem.text.strip()
    except:
        data['question_text'] = ""
        print("    ⚠️ No question text found")
    
    # Answer choices
    try:
        choice_elements = driver.find_elements(By.XPATH, SELECTORS['answer_choices'])
        choices = []
        for choice in choice_elements:
            try:
                letter = choice.find_element(By.CLASS_NAME, "multi-choice").text
                content = choice.find_element(By.CLASS_NAME, "choice-content").text
                choices.append(f"{letter} {content}")
            except:
                choices.append(choice.text.strip())
        data['answer_choices'] = "\n".join(choices)
    except:
        data['answer_choices'] = ""
        print("    ⚠️ No answer choices found")
    
    # Extract answers from result panel
    try:
        correct_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'answer-choice correct')]")
        data['correct_answer'] = correct_elem.get_attribute("data-value")
    except:
        data['correct_answer'] = "Unknown"
    
    try:
        user_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'user-answer') and text()='✓']")
        data['your_answer'] = user_elem.get_attribute("data-value")
    except:
        data['your_answer'] = "Unknown"
    
    # Solution/Explanation
    try:
        solution_elem = driver.find_element(By.XPATH, SELECTORS['solution'])
        data['explanation'] = solution_elem.text.strip()
    except:
        data['explanation'] = ""
    
    # Result extraction
    try:
        result_elem = driver.find_element(By.XPATH, "//span[contains(@class, 'message')]")
        data['result'] = result_elem.text.strip()
    except:
        data['result'] = "Unknown"
    
    # Skills extraction
    try:
        skill_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'tag')]")
        data['content_skills'] = ", ".join([elem.text for elem in skill_elements if elem.text])
    except:
        data['content_skills'] = ""
    
    return data

def scrape_all_questions():
    """Enhanced scraper with robust navigation."""
    service = FirefoxService(executable_path='./geckodriver.exe')
    options = webdriver.FirefoxOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Firefox(service=service, options=options)
    driver.implicitly_wait(10)
    
    try:
        print("Navigate to first question, click browser window for focus, then press Enter...")
        input()
        
        # Get total questions
        try:
            counter = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, SELECTORS['question_counter']))
            )
            counter_text = counter.text.strip()
            if ' of ' in counter_text:
                total = int(counter_text.split(' of ')[1])
            else:
                raise ValueError("Counter format unexpected")
        except:
            total = int(input("Enter total questions (230): ") or "230")
        
        print(f"Scraping {total} questions...")
        results = []
        
        for i in range(total):
            print(f"Question {i+1}/{total}")
            
            # Extract current question data
            data = extract_data(driver, i+1)
            results.append(data)
            
            # Periodic save
            if (i + 1) % 10 == 0:
                with open(f'mcat_partial_{i+1}.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"  💾 Saved progress: {i+1} questions")
            
            # Navigate to next question using arrow keys
            if i < total - 1:
                print(f"  → Navigating to question {i+2}")
                
                # Use arrow key navigation
                if navigate_next(driver):
                    if wait_for_page_change(driver, i+1):
                        continue
                    else:
                        print("  ⚠️ Navigation timeout - continuing anyway")
                else:
                    print("  ❌ Arrow navigation failed")
                    manual_nav = input("  Press Enter after manual navigation, or 'q' to quit: ")
                    if manual_nav.lower() == 'q':
                        break
        
        # Final save
        with open('mcat_complete.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Extraction complete: {len(results)} questions")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_all_questions()