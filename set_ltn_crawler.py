import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from requests_html import AsyncHTMLSession
asession = AsyncHTMLSession()

keyword = "賴品妤"
idx = 1
keepgoing = True
urls = []
while keepgoing:
    keepgoing = False
    res = await asession.get(f"https://www.setn.com/m/search.aspx?q={keyword}&p={idx}")
    soup = BeautifulSoup(res.text, "lxml")
    for url in soup.select("a.gt"):
        if keyword in url["href"]:
            urls.append(f'https://www.setn.com/{url["href"]}')
            keepgoing = True
    idx += 1

news = []
for url in urls:
    new = {}
    text = requests.get(url).text
    soup = BeautifulSoup(text, "lxml")
    new["title"] = soup.select_one("title").text.replace("\r", "").replace("\n", "").replace("\t", "")
    new["date"] = str(soup).split("datePublished")[1].split("T")[0].split('"')[-1]
    content = ""
    for sentence in soup.select("p"):
        content += sentence.text
    new["content"] = content
    news.append(new)

pd.DataFrame(news).to_csv(f"{keyword}_三立新聞.csv", encoding="utf-8-sig", index=False)


idx = 1
keepgoing = True
urls = []
while keepgoing:
    keepgoing = False
    text = requests.get(f"https://search.ltn.com.tw/list?keyword={keyword}&start_time=20170101&end_time=20220816&sort=date&type=all&page={idx}").text
    soup = BeautifulSoup(text, "lxml")
    for url in soup.select("a.ph"):
        urls.append(url["href"])
        keepgoing = True
    idx += 1
    
news = []
for url in tqdm(urls):
    try:
        new = {}
        text = requests.get(url).text
        soup = BeautifulSoup(text, "lxml")
        new["title"] = soup.select_one("h1").text
        new["date"] = soup.select_one("span.time").text.replace("\n", "").strip()
        soup = soup.select_one("div.whitecon")
        content = ""
        for s in soup.select("p"):
            if not s.has_attr('class'):
                content += (s.text)
        new["content"] = content
        news.append(new)
    except:
        pass

pd.DataFrame(news).to_csv(f"{keyword}_自由新聞.csv", encoding="utf-8-sig", index=False)
