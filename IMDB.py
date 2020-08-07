#!/usr/bin/env python3

# Original Post: https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1

__author__ = "Jugal Kishore"
__version__ = "1.0"

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get
import subprocess
import os


def newline():
    print("")


original_post = "https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1"
name = []
links = []
base_url = "https://www.imdb.com"
current_year = datetime.now().year
url = "http://www.imdb.com/search/title?release_date=" + str(current_year) + "," + str(current_year) + "&title_type=feature"


def fetch_movie():
    headers = {"User-Agent": "Mozilla/5.0"}
    print("Year:", current_year)
    newline()
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


def print_list():
    file = open("temp.csv", "w")
    file.write("Rank, Movie Name\n\n")
    i = 0
    while i < 50:
        file.write("{0}, {1}\n".format(i + 1, name[i]))
        i += 1
    file.close()
    subprocess.call(["csvtomd", "temp.csv"])
    os.remove("temp.csv")


def to_csv():
    file = open("Data/data.csv", "w")
    file.write("rank, movieName, link\n\n")
    file.close()
    file = open("Data/data.csv", "a")
    i = 0
    while i < 50:
        file.write("{0}, {1}, {2}\n".format(i + 1, name[i], links[i]))
        i += 1
    file.close()


def to_md():
    file = open("README.md", "w")
    file.write("# Top IMDB 50 Movies Data Scrapper\n\n")
    file.close()
    file = open("README.md", "a")
    file.write("**Original Post:** " + original_post + "\n")
    file.write("\n**Top 50 Movies as of:** {0}\n\n".format(datetime.now().date()))
    file.write("**Link --->** {0}\n\n".format(url))
    file.write("**CSV Data File:** [here](/Data/data.csv)\n\n")
    file.write("**JSON Data File:** [here](/Data/data.json)\n\n")
    i = 0
    while i < 50:
        file.write("**{0} --->** [{1}]({2})\n\n".format(i + 1, name[i], links[i]))
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
print_list()
newline()
print("Original Post: " + original_post)
