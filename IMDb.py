#!/usr/bin/env python3
"""
IMDb Top Movies/TV Shows Data Scraper

Original Post: https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1
Author: Jugal Kishore
Version: 3.0
"""

import json
import os
import subprocess
import sys
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
IMDB_POPULAR_MOVIES_URL = "https://www.imdb.com/chart/moviemeter/"
IMDB_TV_SEARCH_URL = f"https://www.imdb.com/search/title/?title_type=tv_series&release_date={CURRENT_YEAR}-01-01,{CURRENT_YEAR}-12-31"
IMDB_TOP_250_TV_URL = "https://www.imdb.com/chart/toptv/"
IMDB_POPULAR_TV_URL = "https://www.imdb.com/chart/tvmeter/"

# Custom headers
HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
}


def fetch_popular_movies() -> list[dict]:
    """
    Fetch information about popular movies from IMDb.

    Returns:
        list of dict: A list where each dictionary contains Movie information,
        such as the Movie's name, link, and rating.
    """
    print(
        f"Fetching Popular Movies {CURRENT_YEAR} from IMDb ->", IMDB_POPULAR_MOVIES_URL
    )

    movie_data = []

    response = get(IMDB_POPULAR_MOVIES_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    json_data = json.loads(soup.find("script", type="application/ld+json").text)
    for movie in json_data["itemListElement"]:
        movie_name = movie["item"]["name"]
        try:
            movie_rating = movie["item"]["aggregateRating"]["ratingValue"]
        except KeyError:
            movie_rating = 0
        movie_link = movie["item"]["url"]
        movie_data.append(
            {"name": movie_name, "rating": movie_rating, "link": movie_link}
        )
    return movie_data


def fetch_top_50_movies() -> list[dict]:
    """
    Fetch information about the Top 50 Movies of the current year from IMDb.

    Returns:
        list of dict: A list where each dictionary contains Movie information,
        such as the Movie's name and link.
    """
    print(f"Fetching Top 50 Movies {CURRENT_YEAR} from IMDb ->", IMDB_MOVIES_SEARCH_URL)

    movie_data = []

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
        movie_data.append(
            {
                "name": movie["originalTitleText"],
                "link": IMDB_BASE_URL + "/title/" + movie["titleId"] + "/",
                "rating": movie["ratingSummary"]["aggregateRating"],
            }
        )
    return movie_data


def fetch_top_250_movies():
    """
    Fetch the Top 250 Movies from IMDb and save them to a CSV file.
    """
    print(f"Fetching Top 250 Movies from IMDb     ->", IMDB_TOP_250_MOVIES_URL)
    fname = "data/top250/movies.csv"
    ensure_path_directory(fname)

    response = get(IMDB_TOP_250_MOVIES_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    json_data = json.loads(
        soup.find("script", attrs={"type": "application/ld+json"}).text
    )

    file = open(fname, "w")
    file.write("Rank, Movie Name, IMDb Rating, Movie Link\n\n")
    file.close

    file = open(fname, "a")
    i = 1
    for movie in json_data["itemListElement"]:
        movie_rank = i
        movie_name = movie["item"]["name"]
        movie_rating = movie["item"]["aggregateRating"]["ratingValue"]
        movie_link = movie["item"]["url"]
        file.write(
            f'"{movie_rank}", "{movie_name}", "{movie_rating}", "{movie_link}"\n'
        )
        i += 1
    file.close


def fetch_top_50_shows() -> list[dict]:
    """
    Fetch information about the Top 50 Shows of the current year from IMDb.

    Returns:
        list of dict: A list where each dictionary contains TV Show information,
        such as the TV Show's name and link.
    """
    print(f"Fetching Top 50 shows {CURRENT_YEAR} from IMDb  ->", IMDB_TV_SEARCH_URL)

    show_data = []

    response = get(IMDB_TV_SEARCH_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    json_data = (
        json.loads(soup.find("script", id="__NEXT_DATA__").text)
        .get("props", {})
        .get("pageProps", {})
        .get("searchResults", {})
        .get("titleResults", {})
        .get("titleListItems")
    )
    for show in json_data:
        show_data.append(
            {
                "name": show["originalTitleText"],
                "link": IMDB_BASE_URL + "/title/" + show["titleId"] + "/",
                "rating": show["ratingSummary"]["aggregateRating"],
            }
        )
    return show_data


def fetch_top_250_tv():
    """
    Fetch the Top 250 TV Shows from IMDb and save them to a CSV file.
    """
    print(f"Fetching Top 250 TV Shows from IMDb   ->", IMDB_TOP_250_TV_URL)
    fname = "data/top250/shows.csv"
    ensure_path_directory(fname)

    response = get(IMDB_TOP_250_TV_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    json_data = json.loads(
        soup.find("script", attrs={"type": "application/ld+json"}).text
    )

    file = open(fname, "w")
    file.write("Rank, Show Name, IMDb Rating, Show Link\n\n")
    file.close

    file = open(fname, "a")
    i = 1
    for show in json_data["itemListElement"]:
        show_rank = i
        show_name = show["item"]["name"]
        show_rating = show["item"]["aggregateRating"]["ratingValue"]
        show_link = show["item"]["url"]
        file.write(f'"{show_rank}", "{show_name}", "{show_rating}", "{show_link}"\n')
        i += 1
    file.close


def print_top_50_movies(movies_data):
    """
    Print the Top 50 Movie names.

    Args:
        movies_data (list of dict): A list where each dictionary contains movie information,
        such as the Movie's name and link.
    """

    file = open("temp.csv", "w")
    file.write("Rank; Movie Name; Movie Link\n\n")
    for i, movie in enumerate(movies_data[:50], 1):
        file.write(f'"{i}"; "{movie["name"]}"; "{movie["link"]}"\n')
    file.close()

    subprocess.call(["csvtomd", "-d", ";", "temp.csv"])
    os.remove("temp.csv")


def ensure_path_directory(full_path):
    """
    Function to ensure that the directory exists for any given path.

    Args:
        full_path (str): The full path of the directory.
    """
    directory = os.path.dirname(full_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_to_csv(fetched_data, file_path, content_type):
    """
    Save fetched data to a CSV file.

    Args:
        fetched_data (list of dict): A list where each dictionary contains Movie/Show information,
        such as the Movie/Show's name and link.
        file_path (str): The file path where the data should be saved.
    """
    ensure_path_directory(file_path)
    if content_type == "movies":
        header = "Rank, Movie Name, IMDb Rating, Link"
    else:
        header = "Rank, Show Name, IMDb Rating, Link"

    file = open(file_path, "w")
    file.write(header + "\n\n")
    file.close()

    file = open(file_path, "a")
    for i, item in enumerate(fetched_data, 1):
        file.write(f'"{i}", "{item["name"]}", "{item["rating"]}", "{item["link"]}"\n')
    file.close()


def save_to_md(fetched_data):
    """
    Save Movie data to a Markdown file.

    Args:
        fetched_data (list of dict): A list where each dictionary contains Movie/Show information,
        such as the Movie/Show's name and link.
    """
    file = open("README.md", "w")
    file.write("# IMDb Top 50 & 250 Movie/TV Show Data Scraper\n\n")
    file.close()

    file = open("README.md", "a")
    file.write(f"## Original Medium Post: [Link]({ORIGINAL_POST_URL})\n")
    file.write(f"\n**Top IMDb Movies as of:** {datetime.now().date()}\n\n")
    file.write(f"**IMDb Top 50 Movies Page:** [Link]({IMDB_MOVIES_SEARCH_URL})\n\n")
    file.write(f"**IMDb Top 250 Movies Page:** [Link]({IMDB_TOP_250_MOVIES_URL})\n\n")
    file.write(
        "**Top 50 Movies:** [CSV File](/data/top50/movies.csv), [JSON File](/data/top50/movies.json)\n\n"
    )
    file.write(
        "**Top 250 Movies:** [CSV File](/data/top250/movies.csv), [JSON File](/data/top250/movies.json)\n\n"
    )
    file.write(
        "**Top 50 TV Shows:** [CSV File](/data/top50/shows.csv), [JSON File](/data/top50/shows.json)\n\n"
    )
    file.write(
        "**Top 250 TV Shows:** [CSV File](/data/top250/shows.csv), [JSON File](/data/top250/shows.json)\n\n"
    )
    file.write("---\n\n")
    file.write("## IMDb Top 50 Movies List\n\n")

    for i, item in enumerate(fetched_data, 1):
        file.write(f"{i}. [{item["name"]}]({item["link"]})\n\n")

    file.close()


if __name__ == "__main__":
    print("/// IMDb Top 50 & 250 Movie/TV Show Data Scraper ///")
    print("")
    print(f"Original Medium Post: {ORIGINAL_POST_URL}")
    print("")
    fetched_movies = fetch_top_50_movies()
    save_to_csv(fetched_movies, "data/top50/movies.csv", "movies")
    save_to_md(fetched_movies)
    fetch_top_250_movies()

    fetched_shows = fetch_top_50_shows()
    save_to_csv(fetched_shows, "data/top50/shows.csv", "shows")
    fetch_top_250_tv()

    fetched_popular_movies = fetch_popular_movies()
    save_to_csv(fetched_popular_movies, "data/popular/movies.csv", "movies")

    if sys.version_info < (3, 10):
        print_top_50_movies(movie_names, movie_links)
    print("")
    print(f"Original Medium Post: {ORIGINAL_POST_URL}")
