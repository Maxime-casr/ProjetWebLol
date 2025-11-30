import re
import time
from urllib.parse import urljoin
from scrapy import Spider, Request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class ChampionBuildsSpider(Spider):
    name = 'champion_builds'
    
    start_urls = [
        'https://u.gg/lol/champions',
    ]
    
    slug_rx = re.compile(r"/lol/champions/([a-z0-9\-]+)")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processed_slugs = set()
    
    def parse(self, response):
        slugs = self._get_slugs_from_ugg(response.url)
        self.logger.info(f'Trouvé {len(slugs)} slugs de champions')
        
        for slug in sorted(slugs):
            if slug not in self.processed_slugs:
                self.processed_slugs.add(slug)
                pb_url = f'https://probuildstats.com/champion/{slug}'
                yield Request(pb_url, callback=self.parse_probuild, meta={'slug': slug})
    
    def _get_slugs_from_ugg(self, url):
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        
        try:
            self.logger.info(f'Selenium chargement {url}')
            driver.get(url)
            time.sleep(2)
            
            self.logger.info('Défilement pour charger tous les champions')
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(20): 
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.3)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            hrefs = driver.execute_script("""
                const links = new Set();
                document.querySelectorAll('a[href*="/champions/"]').forEach(a => {
                    const href = a.getAttribute('href');
                    if (href && href.match(/\\/lol\\/champions\\/[a-z0-9\\-]+\\/build/)) {
                        links.add(href);
                    }
                });
                return Array.from(links);
            """)
            
            self.logger.info(f'Trouvé {len(hrefs)} liens de champions')
            
            slugs = set()
            for href in hrefs:
                m = self.slug_rx.search(href)
                if m:
                    slug = m.group(1).lower()
                    slugs.add(slug)
            
            self.logger.info(f'{len(slugs)}')
            return slugs
        except Exception as e:
            self.logger.error(f'Erreur: {e}')
            return set()
        finally:
            driver.quit()
    
    def parse_probuild(self, response):
        slug = response.meta.get('slug')
        item_data = self._get_items_from_probuild(response.url, slug)
        
        if item_data:
            yield {
                'champion': slug,
                'popular_items': item_data
            }
    
    def _get_items_from_probuild(self, url, champion_name):
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        prefs = {"profile.managed_default_content_settings.images": 2}
        opts.add_experimental_option('prefs', prefs)
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        
        try:
            self.logger.info(f'Loading items for {champion_name}')
            driver.get(url)
            time.sleep(1.5)
            
            try:
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='/item/']"))
                )
            except Exception:
                time.sleep(1)
            
            items_dict = driver.execute_script("""
                const items = {};
                
                const allText = document.body.innerText;
                if (!allText.includes('Popular Items')) {
                    return {};
                }
                
                const imgs = document.querySelectorAll("img[src*='/item/']");
                
                imgs.forEach(img => {
                    try {
                        let name = img.getAttribute('alt') || img.getAttribute('title') || '';
                        
                        if (!name || name.length < 2) {
                            const src = img.getAttribute('src') || '';
                            if (src.includes('/item/')) {
                                name = src.split('/item/')[1].split('.')[0];
                            }
                        }
                        
                        if (name.length < 2) return;
                        
                        let pct = null;
                        let el = img;
                        for (let i = 0; i < 15 && el && !pct; i++) {
                            const text = el.innerText || el.textContent || '';
                            const match = text.match(/(\\d+[.,]?\\d*)\\s*%/);
                            if (match && match[1]) {
                                pct = parseFloat(match[1].replace(',', '.'));
                                break;
                            }
                            el = el.parentElement;
                        }
                        
                        if (name && pct && pct > 0 && pct <= 100) {
                            if (!items[name] || pct > items[name]) {
                                items[name] = pct;
                            }
                        }
                    } catch (e) {}
                });
                
                return items;
            """)
            
            self.logger.info(f'Found {len(items_dict)} items with percentages for {champion_name}')
            
            if not items_dict:
                self.logger.warning(f'Pas ditems trouver pour{champion_name}')
            
            sorted_items = sorted(items_dict.items(), key=lambda x: x[1], reverse=True)
            return [{'item': name, 'percentage': pct} for name, pct in sorted_items[:6]]
        
        except Exception as e:
            self.logger.error(f'Erreur{champion_name}: {e}')
            return []
        finally:
            driver.quit()
