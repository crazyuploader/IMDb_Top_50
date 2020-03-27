#!/usr/bin/env python3

# Original Post: https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1

__author__ = "Jugal Kishore"
__version__ = "1.0"

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get


def newline():
    print("")


print("///IMDB Top 50 Movies Data Scrapper///")
newline()
current_year = datetime.now().year
headers = {"User-Agent": "Mozilla/5.0"}
start_year = 1990
for year in range(start_year, current_year + 1):
    print("----------------------")
    print("| Current Year:", year, "|")
    print("----------------------")
    newline()
    url = "http://www.imdb.com/search/title?release_date=" + str(year) + "," + str(year) + "&title_type=feature"
    print("Data from Page URL:", url)
    newline()
    response = get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    article = soup.find("div", attrs={"class": "article"}).find("h1")
    print(article.contents[0] + ": ")
    newline()
    lister_list_contents = soup.find("div", attrs={"class": "lister-list"})
    i = 1
    movieList = soup.findAll("div", attrs={"class": "lister-item mode-advanced"})
    for div_item in movieList:
        div = div_item.find("div", attrs={"class": "lister-item-content"})
        header = div.findChildren("h3", attrs={"class": "lister-item-header"})
        print("-------------")
        print("|", i, "Movie: | " + str((header[0].findChildren("a"))[0].contents[0].encode("utf-8").decode("ascii", "ignore")))
        print("-------------")
        newline()
        i += 1
print("Original Post: https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1")
