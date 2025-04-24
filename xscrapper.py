import json
import csv
import os
import datetime
import sys
import random
import time
from playwright.sync_api import sync_playwright, TimeoutError
from pathlib import Path
from typing import List, Dict, Any, Optional

LICENSE = """
========================================================================================================================================================
                                         ██████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗███████╗██╗  ██╗██╗██╗
                                        ██╔═══██╗██╔══██╗██║██╔═══██╗████╗  ██║██╔════╝██║  ██║██║██║
                                        ██║   ██║██████╔╝██║██║   ██║██╔██╗ ██║███████╗███████║██║██║
                                        ██║   ██║██╔══██╗██║██║   ██║██║╚██╗██║╚════██║██╔══██║██║██║
                                        ╚██████╔╝██║  ██║██║╚██████╔╝██║ ╚████║███████║██║  ██║██║██║
                                        ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝

                                        ╔═════════════════════════════════════════════════════════╗
                                        ║ 🔍  X-Scraper V1.0 by OrionShii 🛰️                       ║
                                        ║     Twitter Data Harvester                              ║
                                        ║     🌐 https://github.com/OrionShii                     ║
                                        ║     © 2025 OrionShii. All Rights Reserved.              ║
                                        ╚═════════════════════════════════════════════════════════╝
========================================================================================================================================================

                            This software is an open-source project by OrionShii and is protected under an open-source license. 
                                Use, distribution, and modification are permitted in accordance with the terms of the applicable license. 
                                    Please give appropriate credit to OrionShii.
                                    """

if __name__ == "__main__":
    print(LICENSE)

class TwitterScraper:
    def __init__(self, headless: bool = True):
        """
        Inisialisasi Twitter Scraper
        
        Args:
            headless: Menjalankan browser dalam mode headless jika True
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.debug_mode = True  # Enable debug mode by default for troubleshooting
        
    def __enter__(self):
        """Context manager entry point."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()
        
    def start(self):
        """Memulai browser dan membuat context."""
        print("Memulai browser...")
        self.playwright = sync_playwright().start()
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-web-security',
            '--disable-setuid-sandbox',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        ]
        
        self.browser = self.playwright.chromium.launch(
            headless=self.headless, 
            args=browser_args
        )
        self.context = self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        )
        state_path = "twitter_auth_state.json"
        if os.path.exists(state_path):
            try:
                self.context = self.browser.new_context(
                    storage_state=state_path,
                    viewport={"width": 1366, "height": 768},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                )
                print(f"Loaded browser state from {state_path}")
            except Exception as e:
                print(f"Failed to load browser state: {e}")
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
        """)
        
        self.page = self.context.new_page()
        self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://twitter.com/',
            'sec-ch-ua': '"Chromium";v="123", "Google Chrome";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
        
        print("Browser berhasil dimulai.")
    
    def debug_screenshot(self, name="debug"):
        """Take a debug screenshot if debug mode is enabled"""
        if self.debug_mode:
            filename = f"{name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            self.page.screenshot(path=filename)
            print(f"Debug screenshot saved to {filename}")
        
    def save_page_content(self, name="page_content"):
        """Save the current page HTML content for debugging"""
        if self.debug_mode:
            filename = f"{name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.page.content())
            print(f"Page content saved to {filename}")
    
    def improved_login(self, username: str, password: str) -> bool:
        """
        Enhanced login method with better error handling and detection mechanisms
        
        Args:
            username: Twitter username or email
            password: Twitter password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            print("Mencoba login ke Twitter dengan metode yang ditingkatkan...")
            self.context.clear_cookies()
            self.page.goto("https://twitter.com/i/flow/login", timeout=30000)
            self.page.wait_for_timeout(4000)  # Wait for page to stabilize
            self.debug_screenshot("login_page_initial")
            if self.page.query_selector('a[data-testid="AppTabBar_Home_Link"]') or self.page.query_selector('a[aria-label="Home"]'):
                print("Already logged in!")
                return True
            try:
                print("Waiting for username field...")
                username_field = self.page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
                
                if not username_field:
                    raise Exception("Username field not found")
                for char in username:
                    username_field.type(char)
                    self.page.wait_for_timeout(random.randint(50, 150))
                
                self.page.wait_for_timeout(1000)
                self.debug_screenshot("after_username_entry")
                clicked = False
                next_button_selectors = [
                    'div[data-testid="auth_next_button"]',
                    'div[data-testid="LoginForm_Forward_Button"]',
                    'div[role="button"]:has-text("Next")',
                    'div[role="button"]:has-text("Berikutnya")'
                ]
                
                for selector in next_button_selectors:
                    if self.page.query_selector(selector):
                        try:
                            self.page.click(selector)
                            print(f"Clicked Next button using selector: {selector}")
                            clicked = True
                            break
                        except Exception as e:
                            print(f"Failed to click {selector}: {e}")
                if not clicked:
                    try:
                        print("Trying JavaScript click method...")
                        self.page.evaluate('''() => {
                            const buttons = Array.from(document.querySelectorAll('div[role="button"]'));
                            const nextButton = buttons.find(button => {
                                const text = button.textContent.toLowerCase();
                                return text.includes('next') || text.includes('berikutnya');
                            });
                            if (nextButton) {
                                nextButton.click();
                                return true;
                            }
                            return false;
                        }''')
                        clicked = True
                    except Exception as e:
                        print(f"JavaScript click failed: {e}")
                self.page.wait_for_timeout(3000)
                self.debug_screenshot("after_next_button")
                if self.page.query_selector('input[data-testid="ocfEnterTextTextInput"]'):
                    print("Detected username verification step")
                    input_field = self.page.query_selector('input[data-testid="ocfEnterTextTextInput"]')
                    if input_field:
                        for char in username:
                            input_field.type(char)
                            self.page.wait_for_timeout(random.randint(50, 150))
                        self.page.wait_for_timeout(1000)
                        for selector in next_button_selectors:
                            if self.page.query_selector(selector):
                                try:
                                    self.page.click(selector)
                                    print(f"Clicked Next button in verification step using: {selector}")
                                    break
                                except:
                                    continue
                        self.page.evaluate('''() => {
                            const buttons = Array.from(document.querySelectorAll('div[role="button"]'));
                            const nextButton = buttons.find(button => {
                                const text = button.textContent.toLowerCase();
                                return text.includes('next') || text.includes('berikutnya');
                            });
                            if (nextButton) nextButton.click();
                        }''')
                        
                        self.page.wait_for_timeout(3000)
                password_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[autocomplete="current-password"]'
                ]
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = self.page.wait_for_selector(selector, timeout=10000)
                        if password_field:
                            print(f"Found password field using selector: {selector}")
                            break
                    except Exception as e:
                        print(f"Selector {selector} not found: {e}")
                
                if not password_field:
                    self.debug_screenshot("password_field_missing")
                    self.save_page_content("password_page_content")
                    print("Password field not found after multiple attempts")
                    if self.page.query_selector('text="Verify your identity"') or self.page.query_selector('text="Verify your phone"'):
                        print("Twitter is requesting additional verification. Please login manually first.")
                    
                    return False
                for char in password:
                    password_field.type(char)
                    self.page.wait_for_timeout(random.randint(50, 150))
                
                self.page.wait_for_timeout(1000)
                self.debug_screenshot("after_password_entry")
                login_button_selectors = [
                    'div[data-testid="LoginForm_Login_Button"]',
                    'div[role="button"]:has-text("Log in")',
                    'div[role="button"]:has-text("Login")',
                    'div[role="button"]:has-text("Masuk")'
                ]
                
                clicked = False
                for selector in login_button_selectors:
                    if self.page.query_selector(selector):
                        try:
                            self.page.click(selector)
                            print(f"Clicked login button using selector: {selector}")
                            clicked = True
                            break
                        except:
                            continue
                if not clicked:
                    print("Using JavaScript to click login button")
                    self.page.evaluate('''() => {
                        const buttons = Array.from(document.querySelectorAll('div[role="button"]'));
                        const loginButton = buttons.find(button => {
                            const text = button.textContent.toLowerCase();
                            return text.includes('log in') || text.includes('login') || text.includes('masuk');
                        });
                        if (loginButton) loginButton.click();
                    }''')
                print("Waiting for login to complete...")
                self.page.wait_for_timeout(6000)
                self.debug_screenshot("after_login_attempt")
                home_selectors = [
                    'a[aria-label="Home"]',
                    'a[data-testid="AppTabBar_Home_Link"]',
                    'div[data-testid="primaryColumn"]',
                    'header[role="banner"]'
                ]
                
                for selector in home_selectors:
                    try:
                        if self.page.wait_for_selector(selector, timeout=5000):
                            print(f"Login confirmed with selector: {selector}")
                            state_path = "twitter_auth_state.json"
                            self.context.storage_state(path=state_path)
                            print(f"Browser state saved to {state_path}")
                            return True
                    except:
                        continue
                error_indicators = [
                    'div:has-text("Wrong password")',
                    'div:has-text("Verify your identity")',
                    'div:has-text("Unusual login")',
                    'div:has-text("We noticed unusual activity")'
                ]
                
                for indicator in error_indicators:
                    if self.page.query_selector(indicator):
                        print(f"Login failed: {indicator} detected")
                        return False
                current_url = self.page.url
                if "twitter.com/home" in current_url:
                    print("Login successful based on URL redirect")
                    state_path = "twitter_auth_state.json"
                    self.context.storage_state(path=state_path)
                    print(f"Browser state saved to {state_path}")
                    return True
                
                print("Login status uncertain - check the debug screenshots")
                return False
                
            except Exception as e:
                print(f"Error during login process: {e}")
                self.debug_screenshot("login_error")
                self.save_page_content("error_page_content")
                return False
                
        except Exception as e:
            print(f"Critical error in login process: {e}")
            self.debug_screenshot("critical_error")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """
        Login ke Twitter menggunakan username dan password
        
        Args:
            username: Username Twitter
            password: Password Twitter
            
        Returns:
            True jika login berhasil, False jika gagal
        """
        login_result = self.improved_login(username, password)
        if not login_result:
            print("Improved login failed, trying the original method as backup...")
            try:
                self.page.goto("https://twitter.com/i/flow/login", wait_until="networkidle", timeout=30000)
                self.page.wait_for_timeout(5000)
                
                self.page.wait_for_selector('input[autocomplete="username"]', timeout=15000)
                self.page.fill('input[autocomplete="username"]', username)
                
                self.debug_screenshot("original_login_username")
                self.page.wait_for_timeout(2000)
                self.page.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('div[role="button"]'));
                    const nextButton = buttons.find(button => 
                        button.textContent.includes('Next') || 
                        button.textContent.includes('Berikutnya'));
                    if (nextButton) nextButton.click();
                }''')
                
                self.page.wait_for_timeout(3000)
                self.debug_screenshot("original_login_after_next")
                
                try:
                    self.page.wait_for_selector('input[name="password"]', timeout=10000)
                    self.page.fill('input[name="password"]', password)
                    
                    self.debug_screenshot("original_login_password")
                    self.page.wait_for_timeout(2000)
                    self.page.evaluate('''() => {
                        const loginBtn = document.querySelector('[data-testid="LoginForm_Login_Button"]');
                        if (loginBtn) loginBtn.click();
                        else {
                            const buttons = Array.from(document.querySelectorAll('div[role="button"]'));
                            const logInButton = buttons.find(button => 
                                button.textContent.includes('Log in') || 
                                button.textContent.includes('Masuk'));
                            if (logInButton) logInButton.click();
                        }
                    }''')
                    
                    try:
                        self.page.wait_for_selector('a[aria-label="Home"]', timeout=15000)
                        print("Login berhasil dengan metode original!")
                        state_path = "twitter_auth_state.json"
                        self.context.storage_state(path=state_path)
                        print(f"State browser disimpan ke {state_path}")
                        
                        return True
                    except Exception as e:
                        print(f"Gagal mendeteksi halaman Home: {e}")
                        self.debug_screenshot("home_detection_failed")
                        return False
                    
                except Exception as e:
                    print(f"Tidak dapat menemukan field password: {e}")
                    self.debug_screenshot("password_field_missing")
                    return False
                
            except Exception as e:
                print(f"Error saat login dengan metode original: {e}")
                self.debug_screenshot("original_login_error")
                return False
                
        return login_result
    
    def check_login_status(self) -> bool:
        """Check if the user is logged in"""
        try:
            current_url = self.page.url
            if not current_url.startswith("https://twitter.com"):
                self.page.goto("https://twitter.com/home", wait_until="domcontentloaded", timeout=15000)
                self.page.wait_for_timeout(3000)
            home_indicators = [
                'a[aria-label="Home"]', 
                'a[data-testid="AppTabBar_Home_Link"]',
                'header[role="banner"]'
            ]
            
            for indicator in home_indicators:
                if self.page.query_selector(indicator):
                    return True
            login_indicators = [
                'a[href="/login"]',
                'a[data-testid="login"]',
                'div[data-testid="loginButton"]'
            ]
            
            for indicator in login_indicators:
                if self.page.query_selector(indicator):
                    return False
            if "twitter.com/i/flow/login" in self.page.url:
                return False
                
            return False  # Default to not logged in if uncertain
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False
    
    def close(self):
        """Menutup browser dan playwright."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def build_search_url(self, keyword: str, lang: Optional[str] = None, 
                         start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """
        Membangun URL pencarian Twitter
        
        Args:
            keyword: Kata kunci untuk pencarian
            lang: Kode bahasa (en, id, dll)
            start_date: Tanggal mulai format YYYY-MM-DD
            end_date: Tanggal akhir format YYYY-MM-DD
            
        Returns:
            URL pencarian Twitter
        """
        base_url = "https://twitter.com/search"
        query_parts = [keyword]
        
        if lang:
            query_parts.append(f"lang:{lang}")
            
        if start_date and end_date:
            start = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            end = datetime.datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            query_parts.append(f"since:{start} until:{end}")
            
        query = " ".join(query_parts)
        search_query = f"{base_url}?q={query}&src=typed_query&f=live"
        return search_query
    
    def human_like_scroll(self):
        """Scroll dengan cara yang lebih agresif untuk mengambil lebih banyak tweet"""
        scroll_distance = random.randint(500, 1200)  # Increased from 300-700
        for i in range(0, scroll_distance, random.randint(100, 200)):  # Larger steps
            self.page.evaluate(f"window.scrollBy(0, {random.randint(80, 150)})")  # Larger scroll increments
            time.sleep(random.uniform(0.05, 0.15))  # Shorter pauses
        self.page.evaluate("window.scrollBy(0, 1000)")  # Force extra scroll at end
        time.sleep(random.uniform(0.3, 0.8))  # Reduced from 0.5-1.5
        try:
            show_more_selectors = [
                'div[role="button"]:has-text("Show more")',
                'div[role="button"]:has-text("Load more")',
                'div[role="button"]:has-text("Show more tweets")'
            ]
            
            for selector in show_more_selectors:
                if self.page.query_selector(selector):
                    self.page.click(selector)
                    time.sleep(1)
                    break
        except:
            pass
        
    def force_reload_tweets(self):
        """Force reload tweets if we're not getting new ones"""
        try:
            self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
            self.page.evaluate("window.scrollTo(0, 2000)")
            time.sleep(1.5)
            
            print("Forced tweet reload")
            return True
        except:
            return False
    
    def scrape_tweets(self, keyword: str, max_tweets: int = 100, lang: Optional[str] = None,
                     start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape tweets berdasarkan kata kunci dan filter
        
        Args:
            keyword: Kata kunci untuk pencarian
            max_tweets: Jumlah tweet maksimal yang akan diambil
            lang: Kode bahasa (en, id, dll)
            start_date: Tanggal mulai format YYYY-MM-DD
            end_date: Tanggal akhir format YYYY-MM-DD
            
        Returns:
            List berisi data tweet
        """
        if not self.check_login_status():
            print("User not logged in. Cannot scrape tweets.")
            return []
        
        search_url = self.build_search_url(keyword, lang, start_date, end_date)
        print(f"Membuka URL pencarian: {search_url}")
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                self.page.goto(search_url, wait_until="networkidle", timeout=30000)
                break
            except Exception as e:
                retry_count += 1
                print(f"Gagal memuat halaman, mencoba lagi ({retry_count}/{max_retries}): {e}")
                time.sleep(2)
                
                if retry_count == max_retries:
                    print("Gagal memuat halaman setelah beberapa percobaan.")
                    self.debug_screenshot("failed_search_page")
                    return []
        
        print(f"Mencari tweet dengan kata kunci: {keyword}")
        if lang:
            print(f"Bahasa: {lang}")
        if start_date and end_date:
            print(f"Periode: {start_date} sampai {end_date}")
        try:
            print("Menunggu tweet dimuat...")
            selectors = [
                'article[data-testid="tweet"]',
                'div[data-testid="tweet"]',
                'div[data-testid="tweetText"]',
                '[data-testid="cellInnerDiv"]'
            ]
            found = False
            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=15000)
                    print(f"Tweet ditemukan dengan selector: {selector}")
                    found = True
                    break
                except:
                    continue
                    
            if not found:
                self.debug_screenshot("no_tweets_found")
                print("Tidak dapat menemukan tweet dengan selectors yang ada.")
                if self.page.query_selector('div[data-testid="loginButton"]'):
                    print("Terdeteksi layar login. Session tidak valid.")
                elif self.page.query_selector('div[data-testid="emptyState"]'):
                    print("Tidak ada hasil untuk pencarian ini.")
                
                return []
                
        except TimeoutError:
            self.debug_screenshot("tweet_load_timeout")
            print("Tidak ada tweet yang ditemukan atau halaman tidak dimuat dengan benar.")
            print("Kemungkinan sesi login tidak valid atau rate limited.")
            return []
        
        tweets_data = []
        last_tweet_count = 0
        
        print(f"Mulai mengumpulkan {max_tweets} tweet...")
        no_new_tweets_count = 0
        attempts = 0
        max_attempts = 15
        
        while len(tweets_data) < max_tweets and no_new_tweets_count < 100  and attempts < max_attempts:
            attempts += 1
            tweet_elements = self.page.query_selector_all('article[data-testid="tweet"]')
            if not tweet_elements or len(tweet_elements) == 0:
                try:
                    tweet_elements = self.page.query_selector_all('div[data-testid="cellInnerDiv"] div[data-testid="tweet"]')
                except:
                    pass
            if not tweet_elements or len(tweet_elements) == 0:
                print("Tidak ada tweet yang ditemukan dengan selectors yang tersedia.")
                if attempts > 3:  # Only take screenshot after a few attempts
                    self.debug_screenshot("no_tweets_found_while_scrolling")
                    break
                else:
                    time.sleep(2)
                    continue
            for i in range(last_tweet_count, len(tweet_elements)):
                if len(tweets_data) >= max_tweets:
                    break
                    
                tweet = tweet_elements[i]
                
                try:
                    username = "Unknown"
                    timestamp = ""
                    text = ""
                    tweet_id = ""
                    metrics = {}
                    username_selectors = [
                        'div[data-testid="User-Name"] a span',
                        'div[data-testid="User-Name"] span',
                        'a[role="link"] div span span',
                        '[data-testid="User-Name"] a[tabindex="-1"] span'
                    ]
                    
                    for selector in username_selectors:
                        try:
                            username_element = tweet.query_selector(selector)
                            if username_element:
                                username = username_element.text_content().strip()
                                if username and username != "Unknown":
                                    break
                        except:
                            continue
                    try:
                        time_element = tweet.query_selector('time')
                        if time_element:
                            timestamp = time_element.get_attribute('datetime')
                    except:
                        timestamp = ""
                    try:
                        text_element = tweet.query_selector('div[data-testid="tweetText"]')
                        if text_element:
                            text = text_element.inner_text()
                    except:
                        text = ""
                    try:
                        link_elements = tweet.query_selector_all('a[href*="/status/"]')
                        for link in link_elements:
                            href = link.get_attribute('href')
                            if href and '/status/' in href:
                                tweet_id = href.split('/status/')[1].split('/')[0]
                                break
                    except:
                        tweet_id = ""
                    metrics_selectors = {
                        "likes": ['div[data-testid="like"]', 'div[aria-label*="Like"]'],
                        "retweets": ['div[data-testid="retweet"]', 'div[aria-label*="Retweet"]'],
                        "replies": ['div[data-testid="reply"]', 'div[aria-label*="Reply"]']
                    }
                    
                    for metric_name, selectors in metrics_selectors.items():
                        for selector in selectors:
                            try:
                                element = tweet.query_selector(selector)
                                if element:
                                    text_content = element.text_content().strip()
                                    if text_content:
                                        metrics[metric_name] = text_content
                                    break
                            except:
                                continue
                    if text and username != "Unknown":
                        tweets_data.append({
                            "username": username,
                            "timestamp": timestamp,
                            "text": text,
                            "tweet_id": tweet_id,
                            "metrics": metrics,
                            "keyword": keyword
                        })
                        
                        print(f"Tweet {len(tweets_data)}/{max_tweets} diambil dari @{username}")
                    
                except Exception as e:
                    print(f"Error saat mengekstrak data tweet: {e}")
            if last_tweet_count == len(tweet_elements):
                no_new_tweets_count += 1
            else:
                no_new_tweets_count = 0
                
            last_tweet_count = len(tweet_elements)
            if len(tweets_data) >= max_tweets:
                break
            self.human_like_scroll()
            time.sleep(random.uniform(1.0, 3.0))
                    
        return tweets_data
    
    def export_to_csv(self, tweets_data: List[Dict[str, Any]], filename: str = "tweets.csv"):
        """
        Ekspor data tweet ke file CSV
        
        Args:
            tweets_data: List berisi data tweet
            filename: Nama file CSV
        """
        if not tweets_data:
            print("Tidak ada data untuk diekspor.")
            return
            
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'timestamp', 'text', 'tweet_id']
            if 'metrics' in tweets_data[0] and tweets_data[0]['metrics']:
                for metric in tweets_data[0]['metrics']:
                    fieldnames.append(f"metrics_{metric}")
                    
            fieldnames.append('keyword')
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for tweet in tweets_data:
                row = {
                    'username': tweet['username'],
                    'timestamp': tweet['timestamp'],
                    'text': tweet['text'],
                    'tweet_id': tweet['tweet_id'],
                    'keyword': tweet['keyword']
                }
                if 'metrics' in tweet and tweet['metrics']:
                    for k, v in tweet['metrics'].items():
                        row[f"metrics_{k}"] = v
                        
                writer.writerow(row)
                
        print(f"Data berhasil diekspor ke {filename}")
    
    def export_to_json(self, tweets_data: List[Dict[str, Any]], filename: str = "tweets.json"):
        """
        Ekspor data tweet ke file JSON
        
        Args:
            tweets_data: List berisi data tweet
            filename: Nama file JSON
        """
        if not tweets_data:
            print("Tidak ada data untuk diekspor.")
            return
            
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(tweets_data, jsonfile, ensure_ascii=False, indent=4)
            
        print(f"Data berhasil diekspor ke {filename}")

def is_valid_date(date_string):
    """Validasi format tanggal YYYY-MM-DD"""
    try:
        datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def get_user_input():
    """Mendapatkan input dari pengguna untuk parameter scraping"""
    print("\n=== Parameter Pencarian ===")
    use_saved_credentials = False
    credentials_file = "twitter_credentials.json"
    twitter_username = ""
    twitter_password = ""
    
    if os.path.exists(credentials_file):
        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
                twitter_username = creds.get('username', '')
                twitter_password = creds.get('password', '')
                
            if twitter_username and twitter_password:
                use_saved = input(f"Gunakan kredensial tersimpan untuk @{twitter_username}? (y/n, default: y): ").lower() != "n"
                if use_saved:
                    use_saved_credentials = True
        except:
            pass
    
    if not use_saved_credentials:
        print("\n=== Login Twitter ===")
        print("Kredensial ini akan digunakan untuk login dan tidak akan dibagikan.")
        twitter_username = input("Username atau Email Twitter: ")
        twitter_password = input("Password Twitter: ")
        
        save_creds = input("Simpan kredensial untuk penggunaan berikutnya? (y/n, default: n): ").lower() == "y"
        if save_creds:
            try:
                with open(credentials_file, 'w') as f:
                    json.dump({
                        'username': twitter_username,
                        'password': twitter_password
                    }, f)
                print(f"Kredensial disimpan ke {credentials_file}")
            except Exception as e:
                print(f"Error menyimpan kredensial: {e}")
    keyword = input("\nKata kunci pencarian: ")
    while not keyword:
        print("Kata kunci tidak boleh kosong.")
        keyword = input("Kata kunci pencarian: ")
    lang = input("Bahasa (en/id/kosongkan untuk semua): ").lower()
    if lang and lang not in ["en", "id"]:
        print("Kode bahasa tidak valid. Menggunakan default (semua bahasa).")
        lang = None
    use_date = input("Gunakan filter tanggal? (y/n): ").lower() == "y"
    start_date = None
    end_date = None
    
    if use_date:
        start_date = input("Tanggal mulai (YYYY-MM-DD): ")
        while not is_valid_date(start_date):
            print("Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")
            start_date = input("Tanggal mulai (YYYY-MM-DD): ")
        
        end_date = input("Tanggal akhir (YYYY-MM-DD): ")
        while not is_valid_date(end_date):
            print("Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")
            end_date = input("Tanggal akhir (YYYY-MM-DD): ")
    max_tweets = input("Jumlah maksimum tweet (default: 100): ")
    try:
        max_tweets = int(max_tweets)
        if max_tweets <= 0:
            print("Jumlah tweet harus positif. Menggunakan default (100).")
            max_tweets = 100
    except ValueError:
        print("Input tidak valid. Menggunakan default (100).")
        max_tweets = 100
    output_format = input("Format output (csv/json, default: csv): ").lower()
    if output_format not in ["csv", "json"]:
        print("Format tidak valid. Menggunakan default (csv).")
        output_format = "csv"
    headless = input("Jalankan dalam mode headless? (y/n, default: y): ").lower() != "n"
    
    return {
        "twitter_username": twitter_username,
        "twitter_password": twitter_password,
        "keyword": keyword,
        "lang": lang if lang else None,
        "start_date": start_date,
        "end_date": end_date,
        "max_tweets": max_tweets,
        "output_format": output_format,
        "headless": headless
    }

def main():
    
    try:
        params = get_user_input()
        
        print("\nMemulai scraping Twitter...")
        with TwitterScraper(headless=params["headless"]) as scraper:
            login_success = scraper.login(params["twitter_username"], params["twitter_password"])
            
            if not login_success:
                print("\nLogin gagal. Tidak dapat melanjutkan.")
                return
                
            tweets = scraper.scrape_tweets(
                keyword=params["keyword"],
                max_tweets=params["max_tweets"],
                lang=params["lang"],
                start_date=params["start_date"],
                end_date=params["end_date"]
            )
            
            if not tweets:
                print("Tidak ada tweet yang ditemukan.")
                print("\nSaran troubleshooting:")
                print("1. Periksa apakah kata kunci terlalu spesifik")
                print("2. Coba tanpa filter tanggal atau bahasa")
                print("3. Gunakan mode non-headless (n) untuk melihat proses scrapernya")
                print("4. Coba lagi nanti jika Twitter sedang rate limiting")
                return
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if params["output_format"] == 'csv':
                filename = f"tweets_{params['keyword'].replace(' ', '_')}_{timestamp}.csv"
                scraper.export_to_csv(tweets, filename)
            else:
                filename = f"tweets_{params['keyword'].replace(' ', '_')}_{timestamp}.json"
                scraper.export_to_json(tweets, filename)
                
            print(f"Berhasil mengambil {len(tweets)} tweet.")
            print(f"Data disimpan ke {filename}")
            
    except KeyboardInterrupt:
        print("\nOperasi dibatalkan oleh pengguna.")
    except Exception as e:
        print(f"\nTerjadi kesalahan: {e}")
        print("Screenshot debug diambil jika tersedia.")

if __name__ == "__main__":
    main()
