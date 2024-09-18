#!/usr/bin/env python3
"""
IMDb Top 50 Movies Data Scraper

Original Post: https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1
Author: Jugal Kishore
Version: 3.0
"""

import json
import os
import subprocess
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup

# Original post link
ORIGINAL_POST_URL = (
    "https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1"
)

# Get current year
CURRENT_YEAR = datetime.now().year

# IMDb URLs
IMDB_BASE_URL = "https://www.imdb.com"
IMDB_MOVIES_SEARCH_URL = f"https://www.imdb.com/search/title/?title_type=feature&release_date={CURRENT_YEAR}-01-01,{CURRENT_YEAR}-12-31"
IMDB_TOP_250_MOVIES_URL = "https://www.imdb.com/chart/top/"

# Custom headers
HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
}


def fetch_top_50_movies():
    """
    Fetch information about the top 50 movies of the current year from IMDb.

    Returns:
        tuple: A tuple containing two lists - movie names and their IMDb links.
    """
    print(f"Fetching top 50 shows {CURRENT_YEAR} from IMDb ->", IMDB_MOVIES_SEARCH_URL)

    name = []
    links = []

    response = get(IMDB_MOVIES_SEARCH_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    json_data = (
        json.loads(soup.find("script", id="__NEXT_DATA__").text)
        .get("props", {})
        .get("pageProps", {})
        .get("searchResults", {})
        .get("titleResults", {})
        .get("titleListItems")
    )
    for movie in json_data:
        name.append(movie["originalTitleText"])
        links.append(IMDB_BASE_URL + "/title/" + movie["titleId"] + "/")
    return name, links


def fetch_top_250_movies():
    """
    Fetch the top 250 movies from IMDb and save them to a CSV file.
    """
    fname = "Data/T250/data.csv"
    got = get(IMDB_TOP_250_MOVIES_URL, headers=HEADERS)
    soup = BeautifulSoup(got.text, "html.parser")

    json_data = json.loads(
        soup.find("script", attrs={"type": "application/ld+json"}).text
    )

    file = open(fname, "w")
    file.write("Rank, Movie Name, Movie Link\n\n")
    file.close

    file = open(fname, "a")
    i = 1
    for movie in json_data["itemListElement"]:
        movie_rank = i
        movie_name = movie["item"]["name"]
        movie_link = movie["item"]["url"]
        file.write(f'"{movie_rank}", "{movie_name}", "{movie_link}"\n')
        i += 1
    file.close


def print_top_50_movies(name, links):
    """
    Print the top 50 movie names.

    Args:
        name (list): A list of movie names.
    """
    file = open("temp.csv", "w")
    file.write("Rank; Movie Name; Movie Link\n\n")
    for i, movie_name in enumerate(name[:50], 1):
        file.write(f'"{i}"; "{movie_name}"; "{links[i - 1]}"\n')
    file.close()

    subprocess.call(["csvtomd", "-d", ";", "temp.csv"])
    os.remove("temp.csv")


def save_to_csv(name, links):
    """
    Save movie data to a CSV file.

    Args:
        name (list): A list of movie names.
        links (list): A list of IMDb links for the movies.
    """
    file = open("Data/T50/data.csv", "w")
    file.write("Rank, Movie Name, Link\n\n")
    file.close()

    file = open("Data/T50/data.csv", "a")
    for i, (movie_name, movie_link) in enumerate(zip(name[:50], links[:50]), 1):
        file.write(f'"{i}", "{movie_name}", "{movie_link}"\n')
    file.close()


def save_to_md(name, links):
    """
    Save movie data to a Markdown file.

    Args:
        name (list): A list of movie names.
        links (list): A list of IMDb links for the movies.
    """
    file = open("README.md", "w")
    file.write("# Top IMDb 50 Movies Data Scraper\n\n")
    file.close()

    file = open("README.md", "a")
    file.write(f"## Original Medium Post: [Link]({ORIGINAL_POST_URL})\n")
    file.write(f"\n**Top IMDb Movies as of:** {datetime.now().date()}\n\n")
    file.write(f"**IMDb Top 50 Movies Page:** [Link]({IMDB_MOVIES_SEARCH_URL})\n\n")
    file.write(f"**IMDb Top 250 Movies Page:** [Link]({IMDB_TOP_250_MOVIES_URL})\n\n")
    file.write("**T50 CSV Data File:** [Link](/Data/T50/data.csv)\n\n")
    file.write("**T50 JSON Data File:** [Link](/Data/T50/data.json)\n\n")
    file.write("**T250 CSV Data File:** [Link](/Data/T250/data.csv)\n\n")
    file.write("**T250 JSON Data File:** [Link](/Data/T250/data.json)\n\n")
    file.write("---\n\n")
    file.write("## IMDb Top 50 Movies List\n\n")

    for i, (movie_name, movie_link) in enumerate(zip(name[:50], links[:50]), 1):
        file.write(f"{i}. [{movie_name}]({movie_link})\n\n")

    file.close()


if __name__ == "__main__":
    print("/// IMDb Top 50 Movies Data Scraper ///")
    print("")
    print(f"Original Post: {ORIGINAL_POST_URL}")
    print("")
    movie_names, movie_links = fetch_top_50_movies()
    fetch_top_250_movies()
    save_to_csv(movie_names, movie_links)
    save_to_md(movie_names, movie_links)
    print_top_50_movies(movie_names, movie_links)
    print("")
    print(f"Original Medium Post: {ORIGINAL_POST_URL}")
