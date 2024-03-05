def scrape_data(url: str) -> dict:
    """
    This function takes a URL as input and returns the scraped data from that URL.
    The data is returned as a dictionary where the keys are the tag names and the values are the text inside those tags.
    """
    from bs4 import BeautifulSoup
    import requests

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Create a dictionary to store the scraped data
    scraped_data = {}

    # Iterate over all tags in the soup object
    for tag in soup.find_all(True):
        # If the tag has a name and some text inside, add it to the dictionary
        if tag.name and tag.text.strip():
            scraped_data[tag.name] = tag.text.strip()

    return scraped_data
