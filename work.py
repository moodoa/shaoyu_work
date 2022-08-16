import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def find_udn_news(search_word):
    infos = []
    keepgoing = True
    page = 1
    while keepgoing:
        content = requests.get(
            f"https://udn.com/api/more?page={page}&id=search:{search_word}&channelId=2&type=searchword"
        ).json()
        for article in content["lists"]:
            article_date = datetime.strptime(
                article["time"]["date"], "%Y-%m-%d %H:%M:%S"
            )
            if article_date > datetime(2017, 1, 1) and article_date < datetime(
                2020, 12, 31
            ):
                info = {}
                info["url"] = article["titleLink"]
                info["cateTitle"] = article["cateTitle"]
                info["title"] = article["title"]
                info["content"] = get_news_content(article["titleLink"])
                info["time"] = article["time"]["date"]
                infos.append(info)
            elif article_date < datetime(2017, 1, 1):
                keepgoing = False
                break
        page += 1

    return infos


def get_news_content(url):
    output = ""
    text = requests.get(url).text
    soup = BeautifulSoup(text, "lxml")
    try:
        for p in soup.select_one("section.article-content__editor").select("p"):
            output += p.text
    except:
        try:
            for p in soup.select("p"):
                output += p.text
        except:
            pass
    return output


# from ckiptagger import data_utils
# data_utils.download_data_gdown("./")
from itertools import combinations
from ckiptagger import WS, POS

ws = WS("./data")
pos = POS("./data")


def collect_come_with(text):
    for mark in ["。", "，", "？", "!"]:
        text = text.replace(mark, "$")
    for mark in ["\r", "\n"]:
        text = text.replace(mark, "")
    sentences = text.split("$")
    box = {}
    come_with = {}
    for sentence in sentences:
        ws_results = ws([sentence])
        pos_results = pos(ws_results)
        temp = []
        for idx in range(len(ws_results[0])):
            if pos_results[0][idx] == "VH" and len(ws_results[0][idx]) > 1:
                if ws_results[0][idx] not in box:
                    box[ws_results[0][idx]] = 1
                else:
                    box[ws_results[0][idx]] += 1

                if len(ws_results[0][idx]) > 1:
                    temp.append(ws_results[0][idx])
                for combi in list(combinations(temp, 2)):
                    sorted(combi)
                    if combi not in come_with:
                        come_with[combi] = 1
                    else:
                        come_with[combi] += 1
    return box, come_with


def process_content(filename):
    data = pd.read_excel(filename)
    data["content"]
    all_box = {}
    all_come_with = {}
    for content in data["content"]:
        box, come_with = collect_come_with(content)
        for k, v in box.items():
            if k not in all_box:
                all_box[k] = v
            else:
                all_box[k] += v
        for k, v in come_with.items():
            if k not in all_come_with:
                all_come_with[k] = v
            else:
                all_come_with[k] += v
    return all_box, all_come_with


def collect_come_with(sentence):
    segs = [
        "VA",
        "VB",
        "VC",
        "VD",
        "VE",
        "VF",
        "VG",
        "VH",
        "VI",
        "VJ",
        "VK",
        "VL",
        "VAC",
        "VCL",
        "VHC",
    ]
    #     segs = ["VH"]
    box = {}
    come_with = {}
    ws_results = ws([sentence])
    pos_results = pos(ws_results)
    temp = []
    for idx in range(len(ws_results[0])):
        if pos_results[0][idx] in segs and len(ws_results[0][idx]) > 1:
            if ws_results[0][idx] not in box:
                box[ws_results[0][idx]] = 1
            else:
                box[ws_results[0][idx]] += 1

            if len(ws_results[0][idx]) > 1:
                temp.append(ws_results[0][idx])
            for combi in list(combinations(temp, 2)):
                sorted(combi)
                if combi not in come_with:
                    come_with[combi] = 1
                else:
                    come_with[combi] += 1
    return box, come_with


def encode_it(come_with):
    encode = {}
    ids = 1
    for word_set, v in all_come_with.items():
        for word in word_set:
            if word not in encode:
                encode[word] = ids
                ids += 1

    data = pd.DataFrame(encode.items())
    data.columns = ["Label", "Id"]
    data.to_csv("semanticnode.csv", encoding="utf-8-sig", index=False)
    return encode


def make_semantic(encode_data):
    source = []
    target = []
    types = []
    weight = []
    for k, v in all_come_with.items():
        source.append(encode_data[k[0]])
        target.append(encode_data[k[1]])
        types.append("Undirected")
        weight.append(v)
    semantic = pd.DataFrame()
    semantic["Source"] = source
    semantic["Target"] = target
    semantic["Type"] = types
    semantic["Weight"] = weight
    semantic.to_csv("semantic.csv", encoding="utf-8-sig", index=False)
    return semantic


all_box, all_come_with = process_content("形容詞測試賴品妤.xlsx")
encode_data = encode_it(all_come_with)
semantic_data = make_semantic(encode_data)
