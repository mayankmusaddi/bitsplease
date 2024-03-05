def scrape_data(url: str) -> dict:
    """
    This function takes a URL as input and returns the scraped data from that URL.
    The function uses Selenium to open the webpage and BeautifulSoup to parse the HTML content.
    It specifically extracts the text from the 'p', 'h1', 'h2', 'h3', and 'a' tags.
    The data is returned as a dictionary where the keys are the tag names and the values are lists of the text inside those tags.

    Parameters:
    url (str): The URL of the webpage to scrape.

    Returns:
    dict: A dictionary where the keys are the tag names ('p', 'h1', 'h2', 'h3', 'a') and the values are lists of the text contents of those tags.
    """
    
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup
    import time

    # Setup the driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Fetch the URL
    driver.get(url)

    # Wait for the page to fully load
    time.sleep(3)

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Close the driver
    driver.quit()

    # Define the tags to scrape
    tags_to_scrape = ['p', 'h1', 'h2', 'h3', 'a']

    # Create a dictionary to store the scraped data
    scraped_data = {}

    # Iterate over the defined tags in the soup object
    for tag_name in tags_to_scrape:
        # If the tag has some text inside, add it to the dictionary
        for tag in soup.find_all(tag_name):
            data = tag.text.strip()
            if data:
                data = data.encode("utf-8", "ignore").decode("utf-8")
                # Append the text to the list of texts for this tag
                if tag_name in scraped_data:
                    scraped_data[tag_name].append(data)
                else:
                    scraped_data[tag_name] = [data]

    return scraped_data
