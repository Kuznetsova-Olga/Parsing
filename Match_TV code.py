import requests
from bs4 import BeautifulSoup
URL = "https://matchtv.ru/articles"
TARGET_WORDS = 40_000
RESULT_FILE = "Матч ТВ_интервью.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"}


def get_soup(url):
    response = requests.get(url, headers=HEADERS)
    return BeautifulSoup(response.text, "html.parser")


def get_article_links(base_url, max_pages=20):
    links = set()
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}" if page > 1 else base_url
        soup = get_soup(url)
        found_on_page = 0
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            if "_NI" in href:
                if href.startswith("/"):
                    href = "https://matchtv.ru" + href
                if href not in links:
                    links.add(href)
                    found_on_page += 1
        if found_on_page == 0:
            break


def extract_remarks(article_url):
    soup = get_soup(article_url)
    remarks = []
    article_body = (
        soup.find("div", class_="p-news-details__body")
        or soup.find("div", class_="p-news-details-body")
        or soup.find("article")
    )
    if article_body is None:
        return []
    for p in article_body.find_all("p"):
        text = p.get_text(strip=True)
        if text.startswith("—"):
            remarks.append(text)
    return remarks


def count_words(text):
    return len(text.split())


def main():
    links = get_article_links(URL)
    if not links:
        return
    all_remarks = []
    total_words = 0
    for i, url in enumerate(links, start=1):
        remarks = extract_remarks(url)
        if remarks:
            for r in remarks:
                all_remarks.append(r)
                total_words += count_words(r)
        else:
            print("Это не интервью")
        if total_words >= TARGET_WORDS:
            break
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        for remark in all_remarks:
            f.write(remark)


if __name__ == "__main__":
    main()
