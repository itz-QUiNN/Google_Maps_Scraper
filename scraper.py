import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Path to your locally downloaded ChromeDriver
chrome_driver_path = "C:/Users/ASUS/Downloads/chromedriver.exe"  # Update this with your local path

# Set up Chrome options
options = Options()
options.add_argument('--headless')  # Run in headless mode for performance
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')

# Set up ChromeDriver Service
service = Service(chrome_driver_path)

# Initialize WebDriver with local ChromeDriver
driver = webdriver.Chrome(service=service, options=options)

def scrape_google_maps(query):
    # Open Google Maps
    driver.get("https://www.google.com/maps")

    # Locate the search box and enter the search query
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(5)  # Wait for the results to load

    # Locate the sidebar container
    sidebar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Results for')]"))
    )
    print(f"Sidebar located for {query}!")

    # Scroll the sidebar to load more results
    try:
        for _ in range(5):  # Adjust the range to scroll more
            driver.execute_script("arguments[0].scrollTop += 300;", sidebar)
            time.sleep(0.5)  # Wait for new results to load
        print(f"Scrolling complete for {query}!")

    except:
        print(f"Scrolling failed for {query}")

    # Extract business details
    results = driver.find_elements(By.CLASS_NAME, 'hfpxzc')
    print(f"Found {len(results)} results for {query}!")

    businesses = []
    final_businesses = []

    for result in results[:10]:  # Limit to the first 10 results
        url = result.get_attribute('href')  # Business URL
        businesses.append(url)

    for business in businesses:
        driver.get(business)
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1"))
        )

        name = driver.find_element(By.XPATH, "//h1[@class='DUwDvf lfPIob']").text

        try:
            address = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Address')]").get_attribute("aria-label")
        except:
            address = "N/A"
        try:
            phone = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Phone')]").get_attribute("aria-label")
        except:
            phone = "N/A"
        try:
            website = driver.find_element(By.XPATH, "//a[@data-item-id='authority']").get_attribute("href")
        except:
            website = "N/A"

        final_businesses.append({
            'name': name,
            'address': address,
            'phone': phone,
            'website': website
        })

    return final_businesses

def save_to_json(data, keyword, filename="businesses_data.json"):
    try:
        # Read existing data from the file
        with open(filename, "r") as file:
            all_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty, start with an empty dictionary
        all_data = {}

    # Add new data to the dictionary with the keyword as the key
    all_data[keyword] = data

    # Write the updated data back to the file
    with open(filename, "w") as file:
        json.dump(all_data, file, indent=4)

# List of keywords to search for
keywords = [
    'Plumber Levittown', 'Plumber Newark'
]

# Loop through the list of keywords
for keyword in keywords:
    print(f"Scraping results for: {keyword}")
    businesses = scrape_google_maps(keyword)
    
    # Save results for each keyword immediately, using the keyword as the key
    save_to_json(businesses, keyword)
    print(f"Results for {keyword} saved to JSON.")


# Close the browser
driver.quit()
