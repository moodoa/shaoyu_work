import requests
from bs4 import BeautifulSoup
import pandas as pd
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
