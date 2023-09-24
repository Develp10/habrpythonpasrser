import random
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json 

CATEGORIES = [
    "https://habr.com/ru/hubs/programming/", 
    "https://habr.com/ru/hubs/python/"
]

with open("proxy.txt") as file:
    PROXY_LIST = "".join(file.readlines()).split("\n")

async def send_request(url, rand_proxy) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=f"http://{rand_proxy}") as resp:
            return await resp.text(encoding="utf-8")
        

async def parse_category(category_url, rand_proxy):
    html_response = await send_request(url=category_url, rand_proxy=rand_proxy)
    soup = BeautifulSoup(html_response, "lxml")
    pagination_block = soup.find("div", class_="tm-pagination__pages")
    pages_count = pagination_block.find_all("a", class_="tm-pagination__pages")[-1].text.strip()
    print(f"category: {category_url} | pages: {pages_count}")

    dict_articles = {}

    for page in range(int(pages_count)):
        page_response = await send_request(
            url=f"{category_url}/page{page}", 
            rand_proxy=rand_proxy
        )

        page_soup = BeautifulSoup(page_response, "lxml")
        articles = page_soup.find_all("article", class_="tm-articles-list__item")

        for article in articles:
            info_block = article.find("a", class_="tm-title__link")
            title = info_block.find("span").text.strip()
            id = int(info_block.get("href").split("/")[-2])
            link = f"https://habr.com{info_block.get('href')}"
            category_name = category_url.split("/")[-1]

            result = f"{category_name} | {title} | {link}\n"

            if id in dict_articles:
                continue
            else:
                dict_articles[id] = result

    with open("dict_articles.json", "w") as file:
        json.dump(dict_articles, file)

    print(dict_articles)


async def main():
    rand_proxy = random.choice(PROXY_LIST)
    data = [parse_category(category, rand_proxy) for category in CATEGORIES]
    await asyncio.gather(*data)


if __name__ == "__main__":
    asyncio.run(main())    