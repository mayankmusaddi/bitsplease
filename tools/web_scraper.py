async def web_scraper(url: str) -> dict:
    """
    This function takes a URL as input and returns the scraped data from that URL.
    The function uses Pyppeteer to open the webpage and BeautifulSoup to parse the HTML content.
    It specifically extracts the text from the 'p', 'h1', 'h2', 'h3', and 'a' tags.
    The data is returned as a dictionary where the keys are the tag names and the values are lists of the text inside those tags.
    Why we're not using Selenium?: It doesn't support asynchronous operations natively.

    Parameters:
    url (str): The URL of the webpage to scrape.

    Returns:
    dict: A dictionary where the keys are the tag names ('p', 'h1', 'h2', 'h3', 'a') and the values are lists of the text contents of those tags.
    """
    try:
        import asyncio
        from pyppeteer import launch
        from bs4 import BeautifulSoup

        # Launch the browser
        browser = await launch(headless=True)
        page = await browser.newPage()

        # Fetch the URL
        await page.goto(url)
        # await page.waitForNavigation(timeout=30000)
        await asyncio.sleep(3)
        # Get the HTML of the page
        html = await page.content()

        # Close the browser
        await browser.close()

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Define the tags to scrape
        tags_to_scrape = ['p', 'h1', 'h2', 'h3', 'a']

        # Create a dictionary to store the scraped data
        scraped_data = {}

        # Iterate over the defined tags in the soup object
        for tag_name in tags_to_scrape:
            # If the tag has some text inside, add it to the dictionary
            for tag in soup.find_all(tag_name):
                if tag.text.strip():
                    # Append the text to the list of texts for this tag
                    if tag_name in scraped_data:
                        scraped_data[tag_name].append(tag.text.strip())
                    else:
                        scraped_data[tag_name] = [tag.text.strip()]
        print(scraped_data)
        return scraped_data
    except Exception as e:
        print(e)
        print(url)
        return url


"""
Usage:
import asyncio
import nest_asyncio

url = "https://realpython.com/python-web-scraping-practical-introduction/"
results = asyncio.get_event_loop().run_until_complete(scrape_data(url))
print(results)
nest_asyncio.apply()
"""
