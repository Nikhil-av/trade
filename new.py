from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Set up headless Chrome
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

url = "https://drive.google.com/file/d/1x5HH_yggl8kwzFivt4tBKI9sa0nPW8I_/view?pli=1"
ss=driver.get(url)
time.sleep(5)  # Wait for content to load

# Scrape visible text
content = driver.page_source
print(content[:5000])  # print partial content

driver.quit()
