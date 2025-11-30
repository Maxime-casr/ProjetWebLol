# Scrapy settings for lol_scraper project

BOT_NAME = 'lol_scraper'

SPIDER_MODULES = ['lol_scraper.spiders']
NEWSPIDER_MODULE = 'lol_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests per domain
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS = 1

# Configure download delay for politeness (reduced for speed)
DOWNLOAD_DELAY = 1

# Disable cookies if not necessary
COOKIES_ENABLED = False

# Disable retries to speed up
RETRY_TIMES = 0

# Custom pipeline
ITEM_PIPELINES = {
    'lol_scraper.pipelines.CollectPipeline': 300,
}

# User agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Log level
LOG_LEVEL = 'INFO'

# Reduce overhead
TELNETCONSOLE_ENABLED = False

# Close spider after finish
SPIDER_AUTOTHROTTLE_ENABLED = False

