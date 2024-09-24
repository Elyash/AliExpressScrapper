from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

PRODUCT_URL = 'https://he.aliexpress.com/item/1005005956410553.html?spm=a2g0o.best.moretolove.2.225c216f6uZIzX&_gl=1*sq3u1s*_gcl_aw*R0NMLjE3MjEyMzcyMjMuQ2p3S0NBancxOTIwQmhBM0Vpd0FKVDNsU2JTeVVqV0dKc05YQzZEWE5GbGZlQ3pUTUZBVDhBZHl1YUJJNXR1bzVuTXV2V3lTUlo4cGNob0N6MGdRQXZEX0J3RQ..*_gcl_dc*R0NMLjE3MjEyMzcyMjMuQ2p3S0NBancxOTIwQmhBM0Vpd0FKVDNsU2JTeVVqV0dKc05YQzZEWE5GbGZlQ3pUTUZBVDhBZHl1YUJJNXR1bzVuTXV2V3lTUlo4cGNob0N6MGdRQXZEX0J3RQ..*_gcl_au*MTk1NTk3NDA2My4xNzI3MDk5Nzcz*_ga*NzI1NjAxMTM1LjE2ODA4MDkyNDg.*_ga_VED1YSGNC7*MTcyNzE4MTU0MC4yMS4xLjE3MjcxODE1NzEuMjkuMC4w&gatewayAdapt=glo2isr'  # Example URL

# Set up Chrome options (headless mode is optional)
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--headless')  # Optional: Remove this to see the browser window
options.add_argument('--disable-dev-shm-usage')

# Set up the WebDriver service
service = Service(ChromeDriverManager().install())

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=service, options=options)

# Go to the AliExpress product page (replace with the product URL)
driver.get(PRODUCT_URL)

# Wait for the page to fully load
time.sleep(5)  # Adjust this based on your network speed

# Extract the product title
try:
    product_title = driver.find_element(By.CLASS_NAME, 'title--wrap--UUHae_g').text
    print(f'Product Title: {product_title}')
except Exception as e:
    print('Product title not found:', e)

# Extract the product price
try:
    product_price = driver.find_element(By.CLASS_NAME, 'price--current--I3Zeidd product-price-current').text
    print(f'Product Price: {product_price}')
except Exception as e:
    print('Product price not found:', e)

# Close the WebDriver
driver.quit()
