
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_p = mars_news(browser)
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_images":hemisphere_images(browser)
    }
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first <a> tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    return news_title, news_p

# ## Featured Images
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    try:
    # Find and click the full image button
        full_image_elem = browser.find_by_tag('button')[1]
        full_image_elem.click()

        # Parse the resulting html with soup
        html = browser.html
        img_soup = soup(html, 'html.parser')

        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

    # ## Mars Facts
def mars_facts():
    df = pd.read_html('https://galaxyfacts-mars.com')[0]
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    return df.to_html()

def hemisphere_images(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hem_img_soup = soup(html, 'html.parser')
    product_links = hem_img_soup.find_all("a", class_="itemLink product-item")
    
    # remove duplicate links of the same css class
    product_links = list(filter(lambda p: p.find("h3") == None, product_links) )

    for link in product_links:
        browser.visit(f'{url}{link.get("href")}')
        html = browser.html
        high_rez_soup = soup(html, 'html.parser')
        img_href = high_rez_soup.find("a",string="Sample").get("href")

        # clean text
        img_text = link.find("img").get("alt").replace(" Enhanced thumbnail","")

        img_url = f'{url}{img_href}'

        hemisphere_image_urls.append( 
            {
                "url": img_url,
                "title": img_text
            }
        )
    return hemisphere_image_urls


