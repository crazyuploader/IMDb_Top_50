#!/usr/bin/env python3

# Original Post: https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1

__author__ = "Jugal Kishore"
__version__ = "1.0"

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get
from os import system


def newline():
    print("")


original_post = "https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1"
name = []
links = []
base_url = "https://www.imdb.com"
def fetch_movie():
    current_year = datetime.now().year
    headers = {"User-Agent": "Mozilla/5.0"}
    start_year = current_year
    for year in range(start_year, current_year + 1):
        print("Year:", year)
        newline()
        url = "http://www.imdb.com/search/title?release_date=" + str(year) + "," + str(year) + "&title_type=feature"
        print("Data from Page URL:", url)
        newline()
        response = get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        article = soup.find("div", attrs={"class": "article"}).find("h1")
        print(article.contents[0] + ": ")
        newline()
        i = 1
        movieList = soup.findAll("div", attrs={"class": "lister-item mode-advanced"})
        for div_item in movieList:
            div = div_item.find("div", attrs={"class": "lister-item-content"})
            header = div.findChildren("h3", attrs={"class": "lister-item-header"})
            name.append(str((header[0].findChildren("a"))[0].contents[0].encode("utf-8").decode("ascii", "ignore")))
            links.append("{0}{1}".format(base_url, str((header[0].findChildren("a"))[0]["href"].encode("utf-8").decode("ascii", "ignore"))))
            i += 1


def to_csv():
    file = open("Data/data.csv", "w")
    file.write("Rank, Movie Name\n\n")
    file.close()
    file = open("Data/data.csv", "a")
    i = 0
    while i < 50:
        file.write("{0}, {1}\n".format(i + 1, name[i]))
        i += 1
    file.close()


def to_md():
    file = open("README.md", "w")
    file.write("# Top IMDB 50 Movies Data Scrapper\n\n")
    file.close()
    file = open("README.md", "a")
    file.write("**Original Post:** " + original_post + "\n")
    file.write("\nTop 50 Movies as of: {0}\n\n".format(datetime.now().today()))
    i = 0
    while i < 50:
        file.write("{0} ---> [{1}]({2})\n\n".format(i + 1, name[i], links[i]))
        i += 1
    file.write("**Original Post:** " + original_post + "\n")
    file.close()


print("///IMDB Top 50 Movies Data Scrapper///")
newline()
print("Original Post: " + original_post)
newline()
fetch_movie()
to_csv()
to_md()
system("csvtomd Data/data.csv")
newline()
print("Original Post: " + original_post)
