from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from urllib.request import urlretrieve, URLopener
from bs4 import BeautifulSoup
import os
import re
import requests
import img2pdf


def nh_scrape(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # url = input("Enter the url: ")
    url = url
    driver.get(url)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "lazyload"))
    )

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    page = int(soup.find_all('span', class_='name')[-1].text.strip())
    # print(page)
    
    title = str(soup.find_all('span', class_='pretty')[0].text.strip())
    # print(title)
    
    author_html = soup.find_all("div", class_="tag-container")
    author = ""
    for i in range(len(author_html)):
        if author_html[i].text.strip().startswith("Artists:"):
            author_html = author_html[i]
            break
    for i in author_html.find().find_all(recursive=False):
        author += i.find().text.strip() + ", "
    author = author[:-2]
    # print(author)
    
    tags_html = soup.find_all("div", class_="tag-container")
    tags = ""
    for i in range(len(tags_html)):
        if tags_html[i].text.strip().startswith("Tags:"):
            tags_html = tags_html[i]
            break
    for i in tags_html.find().find_all(recursive=False):
        tags += i.find().text.strip() + ", "
    tags = tags[:-2]
    # print(tags)

    index = soup.find('img', class_='lazyload')['src'].split("/")[4]
    print(f"Starting download of:\n ----------------------------- \n{title}\n\t\tBy {author}\nPages: {page} \nTags: {tags}\n-----------------------------")

    os.mkdir(f'./temp/temp1')

    for i in range(1, page + 1):
        print(f'Downloading page {i} of {page}')
        page_url = f"https://i4.nhentai.net/galleries/{index}/{i}.webp"
        urlretrieve(page_url, f'./temp/temp1/{i}.webp')
        
        # print(page_url)
        # driver.get(page_url)
        
        # WebDriverWait(driver, 10)
        
        # html = driver.page_source
        # soup = BeautifulSoup(html, "html.parser")
        # img = soup.find_all('img')
        # print(soup)
    driver.quit()
    return {"/Title": [title], "/Author": str(author), "/Keywords": tags}, [page], 1




def h2r_scrape(url):
    # ----Grab Metadata: class:list-simple-mini
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # url = input("Enter the url: ")
    url = url
    driver.get(url)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "list-simple-mini"))
    )
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    
    # ----Author = authoer + artist unless both

    author_html = soup.find_all("li", class_="text-primary")
    authors = ""
    for i in range(len(author_html)):
        if author_html[i].find().text.strip().startswith("Author"):
            author_html = author_html[i]
            break
    for i in author_html.find("a"):
        authors += author_html.find("a").text + ", "
        
    artist_html = soup.find_all("li", class_="text-primary")
    artists = ""
    for i in range(len(artist_html)):
        if artist_html[i].find().text.strip().startswith("Artist"):
            artist_html = artist_html[i]
            break
    for i in artist_html.find("a"):
        artists += artist_html.find("a").text + ", "
    if artists == authors:
        artists = ""
    else:
        artists = artists[:-2]
        authors += ", "
    author = authors[:-2] + artists
    
    # ----Title = Grab Head -> link rel alternative
    title_html = soup.find_all("h3", class_="block-title")
    title = ""
    for i in range(len(title_html)):
        if title_html[i].find("i") == None:
            continue
        if "fa-book" in title_html[i].find("i").get("class"):
            title_html = title_html[i]
            break
    title = title_html.find("a").text.strip()
    title = title[:title.find("[")]
    print(title)
    
    
    # ----Keywords = category + content
    tags_html = soup.find_all("li", class_="text-primary")
    category = ""
    for i in range(len(tags_html)):
        if tags_html[i].find().text.strip().startswith("Category"):
            tags_html = tags_html[i]
            break
    for i in tags_html.find_all("a"):
        category += i.text + ", "
        
    tags_html = soup.find_all("li", class_="text-primary")
    content = ""
    for i in range(len(tags_html)):
        if tags_html[i].find().text.strip().startswith("Content"):
            tags_html = tags_html[i]
            break
    for i in tags_html.find_all("a"):
        content += i.text + ", "
    tags = (category + content)[:-2]
    print(tags)
    
    
    # ----Pages = Pages -> If contains / then multiple chapters
    page_html = soup.find_all("li", class_="text-primary")
    num_chapters = 1
    for i in range(len(page_html)):
        if page_html[i].find().text.strip().startswith("Page"):
            page_html = page_html[i].find("a").text.strip()
            break
    if page_html.find("/") != -1:
        ch = page_html[page_html.find("/") + 1 :].strip()
        num_chapters = int(ch[:ch.find(" ")].strip())
        page_html = page_html[:page_html.find("/")].strip()
    page_count = int(page_html[:page_html.find(" ")].strip().replace(",", ""))
    print(page_count)
    print(num_chapters)
    
    
    # ----Chapters = ul nav-chapters
    
    chapter_num = 1
    ch_html = soup.find("ul", class_="nav-chapters")
    titles = []
    pages = []
    for a in list(ch_html.find_all("a"))[::-1]:
        link = a.get("href")
        if "download" not in link and "thumbnails" not in link:
            os.mkdir(f'./temp/temp{chapter_num}')
            subtitle = a.text.strip()
            subtitle = subtitle[subtitle.find('-') + 2:subtitle.find('uploaded by'):]
            print(subtitle)
            print(f"{title.strip()}: {subtitle.strip()}")
            # titles.append(f"{title.strip()}: {subtitle.strip()}".replace(":", "-"))
            titles.append(f"{title.strip()}")
            url = link
            driver.get(url)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "reader-nav"))
            )
            
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            page_html = soup.find("span", class_="page-select_numbers")
            page_count = int(page_html.text[page_html.text.rfind(" ") + 1 ::].strip())
            pages.append(page_count)
            pg_link = soup.find("img", id="arf-reader").get("src")
            for i in range(1, page_count+1):
                page_url = (pg_link[:pg_link.find("ccdn00") + 4] + str(i).rjust(4, "0") + pg_link[pg_link.rfind("."):]).replace(".direct", "cdn.com")
                urlretrieve(page_url, f'./temp/temp{chapter_num}/{i}.jpg')
            chapter_num += 1
                    
            
            
    
    # ----Num page in chapter: span id: js-reader_progress
    # ----Image: img id: arf-reader
    
    return {"/Title": titles, "/Author": str(author), "/Keywords": tags}, pages, page_count

# h2r_scrape("https://hentai2read.com/school_prostitution_journal/")
# nh_scrape("https://nhentai.net/g/616896/")