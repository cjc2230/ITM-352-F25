from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import os
from typing import Dict, Any

# 🛠️ NEW IMPORT: Automatically handles the Chrome driver executable
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
INSTAGRAM_USERNAME = "bestuhm"
INSTAGRAM_PASSWORD = "bestINSTAGRAMF25!"
# Define the path where cookies will be saved (in the same directory as the script)
COOKIES_FILE = "instagram_cookies.json"
# ---------------------

def setup_driver(headless: bool = False) -> webdriver.Chrome:
    """Sets up and returns a basic Chrome WebDriver."""
    print("Setting up Chrome driver...")
    options = Options()
    if headless:
        options.add_argument("--headless")
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(
            service=webdriver.ChromeService(ChromeDriverManager().install()), 
            options=options
        )
        return driver
    except Exception as e:
        print(f"Error setting up WebDriver. Check your Chrome browser installation: {e}")
        raise

def save_cookies(driver: webdriver.Chrome):
    """Saves the current browser session cookies to a local file."""
    try:
        with open(COOKIES_FILE, 'w') as file:
            json.dump(driver.get_cookies(), file)
        print(f"Cookies saved to {COOKIES_FILE}.")
    except Exception as e:
        print(f"Error saving cookies: {e}")

def load_cookies(driver: webdriver.Chrome):
    """Loads cookies from a local file and injects them into the driver."""
    if not os.path.exists(COOKIES_FILE):
        return False
    
    try:
        with open(COOKIES_FILE, 'r') as file:
            cookies = json.load(file)
            driver.get("https://www.instagram.com/") # Must visit the domain first
            for cookie in cookies:
                # Need to remove 'expiry' key if present, as it can be in a float format 
                # that Selenium sometimes rejects (it expects an integer).
                if 'expiry' in cookie:
                    del cookie['expiry'] 
                driver.add_cookie(cookie)
        
        driver.refresh() # Reload the page with cookies injected
        print("Cookies loaded and page refreshed. Checking authentication status...")
        time.sleep(3) 

        # Simple check: If 'Login' button is visible, cookies failed.
        try:
            driver.find_element(By.XPATH, "//button[contains(., 'Log in')]")
            print("Cookies failed: Login button still visible.")
            return False
        except NoSuchElementException:
            print("Cookies successful: Logged in status confirmed.")
            return True
            
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return False

def perform_manual_login(driver: webdriver.Chrome):
    """Performs the login sequence if cookies are not available or failed."""
    print("Performing full login...")
    driver.get("https://www.instagram.com/accounts/login/")
    
    try:
        # 1. Wait for username field
        username_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        password_field = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        
        # Enter credentials
        username_field.send_keys(INSTAGRAM_USERNAME)
        password_field.send_keys(INSTAGRAM_PASSWORD)
        
        # 2. Click the login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # 3. Wait for login to complete (Max 20 seconds)
        WebDriverWait(driver, 20).until(
            EC.url_changes(driver.current_url) 
        )
        print("Login complete. Waiting for pop-ups...")

        # 4. Handle "Save Info" or "Notifications" popups 
        try:
            not_now_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Not Now')]"))
            )
            not_now_button.click()
            time.sleep(1)
            # Try a second time for a potential second popup
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Not Now')]"))
            ).click()
            time.sleep(1)
        except TimeoutException:
            pass 
        
        print("Login process finished.")
        save_cookies(driver)
        return True

    except Exception as e:
        print(f"Manual login failed. Check credentials/selectors: {e}")
        return False


def instagram_login(driver: webdriver.Chrome) -> bool:
    """Tries to log in using cookies, falls back to manual login if necessary."""
    print("\n--- Starting Authentication Process ---")
    if load_cookies(driver):
        return True
    
    if perform_manual_login(driver):
        return True
        
    return False

def get_post_data_simple(driver: webdriver.Chrome, url: str) -> Dict[str, Any]:
    """
    Simulates a post visit, returns MOCK data for both counts and lists to ensure 
    the Matching and Point Calculation logic can be confirmed as working.
    
    Note: Real scraping for counts and lists is currently failing due to Instagram's dynamic loading.
    """
    print(f"\nNavigating to post (SIMULATED): {url}")
    # We skip navigation and extraction since it's unreliable.
    # We wait a moment just to simulate the time a real scrape would take.
    time.sleep(1) 
    
    # --------------------------------------------------------------------------
    # MOCK INTERACTION LISTS: These are the raw usernames we PRETEND to have scraped.
    # These names must be configured to test your fuzzy matching and point logic!
    mock_interactions = {
        # 1. Direct Match: "aiidencc", "bradyj_01", "e1leen.l" (Should match perfectly)
        # 2. Fuzzy Match (Typo): "jennaamari" (Should match the official "jennaamarii" from your CSV)
        # 3. Non-Member Discard: "non_member_a", "non_member_b", "another_non_member" (Should be ignored)
        "likers": ["aiidencc", "non_member_a", "jennaamari", "bradyj_01", "k4nunu", "e1leen.l"],
        "commenters": ["_carleem", "aiidencc", "_carleem", "k4nunu", "aiidencc", "non_member_b"],
        "tagged_users": ["_carleem", "kxchun", "another_non_member"]
    }
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # MOCK COUNTS: We set the counts based on the mock list lengths to ensure non-zero values.
    # This guarantees that the point calculator will receive non-zero inputs.
    likes_count = len(mock_interactions["likers"])
    # Note: Comments include duplicates which are intentional to test the 'comments up to 4' logic.
    comments_count = len(mock_interactions["commenters"]) 
    # --------------------------------------------------------------------------

    post_data = {
        "url": url,
        "raw_counts": {"likes": likes_count, "comments": comments_count},
        "interaction_lists": mock_interactions,
        "error": None
    }
    
    print(f"  -> Successfully returned MOCK data (Counts: L={likes_count}, C={comments_count}) to confirm point calculation.")
    return post_data

# --- Example Execution ---
if __name__ == "__main__":
    driver = None
    try:
        # 1. Setup Driver (Now that cookies are saved, we can switch to headless=True)
        driver = setup_driver(headless=True) 

        # 2. Login (REQUIRED)
        if not instagram_login(driver):
            print("\nFATAL: Failed to log in using both cookies and manual attempt. Exiting.")
        else:
            # 3. Scrape Data 
            # Note: You MUST change this URL to a REAL post you want to test!
            test_post_url = "https://www.instagram.com/p/DPCpgAVEgEP/?img_index=1" 
            scraped_data = get_post_data_simple(driver, test_post_url)
            
            print("\n--- FINAL SCRAPING RESULT ---")
            if scraped_data.get("error"):
                 print(f"Status: {scraped_data['error']}")
            
            # Print the mock counts derived from the mock lists
            print(f"URL: {scraped_data['url']}")
            print(f"Raw LIKES Count (Mock): {scraped_data['raw_counts']['likes']}")
            print(f"Raw COMMENTS Count (Mock): {scraped_data['raw_counts']['comments']}")
            print(f"Commenters List (Mock): {scraped_data['interaction_lists']['commenters']}")

    except Exception as e:
        print(f"\nFATAL ERROR IN MAIN EXECUTION: {e}")
    finally:
        # 4. Cleanup
        if driver:
            print("\nClosing browser.")
            driver.quit()