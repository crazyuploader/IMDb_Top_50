#!/usr/bin/env python3
"""
IMDb Top Movies/TV Shows Data Scraper

Original Post: https://medium.com/@nishantsahoo/which-movie-should-i-watch-5c83a3c0f5b1
Author: Jugal Kishore
Version: 3.0
"""

import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as EC

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
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
}


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-images")
    chrome_options.page_load_strategy = "eager"
    service = EC()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(90)
    driver.implicitly_wait(15)
    return driver


def enrich_title_data(driver, url: str) -> dict:
    """
    Visit an individual IMDb title page and extract additional fields
    from __NEXT_DATA__ that aren't available on listing pages.
    """
    enrichment = {
        "keywords": "",
        "countriesOfOrigin": "",
        "meterRanking": "",
        "meterRankChange": "",
        "directors": "",
        "writers": "",
        "stars": "",
        "topCast": "",
        "budget": "",
        "openingWeekendGross": "",
        "lifetimeGross": "",
        "worldwideGross": "",
        "filmingLocations": "",
        "spokenLanguages": "",
        "soundMix": "",
        "aspectRatio": "",
        "color": "",
        "awardWins": 0,
        "awardNominations": 0,
        "titleType": "",
        "isSeries": False,
        "isEpisode": False,
        "isAdult": False,
    }
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            print(f"    No __NEXT_DATA__ found for {url}")
            return enrichment

        data = json.loads(script.text)
        page_props = data.get("props") or {}
        page_props = page_props.get("pageProps") or {}
        above = page_props.get("aboveTheFoldData") or {}
        main = page_props.get("mainColumnData") or {}

        # Keywords
        kw = above.get("keywords") or {}
        enrichment["keywords"] = ", ".join(
            e["node"]["text"] for e in (kw.get("edges") or [])
        )

        # Countries of origin
        co = above.get("countriesOfOrigin") or {}
        enrichment["countriesOfOrigin"] = ", ".join(
            c["id"] for c in (co.get("countries") or [])
        )

        # Meter ranking (popularity)
        meter = above.get("meterRanking") or {}
        enrichment["meterRanking"] = str(meter.get("currentRank") or "")
        change = meter.get("rankChange")
        if change:
            enrichment["meterRankChange"] = (
                f"{change.get('changeDirection', '')} {change.get('difference', 0)}"
            )

        # Title type metadata
        tt = above.get("titleType") or {}
        enrichment["titleType"] = tt.get("text") or ""
        enrichment["isSeries"] = bool(tt.get("isSeries"))
        enrichment["isEpisode"] = bool(tt.get("isEpisode"))

        enrichment["isAdult"] = bool(above.get("isAdult"))

        # Principal credits (directors, writers, stars)
        credits = above.get("principalCreditsV2") or []
        for group in credits:
            cat = (group.get("grouping") or {}).get("text") or ""
            names = [
                c["name"]["nameText"]["text"]
                for c in (group.get("credits") or [])
                if c.get("name") and c["name"].get("nameText")
            ]
            if cat == "Director":
                enrichment["directors"] = ", ".join(names)
            elif cat == "Writers":
                enrichment["writers"] = ", ".join(names)
            elif cat == "Stars":
                enrichment["stars"] = ", ".join(names)

        # Top cast (up to 5 with character names)
        cast = above.get("castV2") or {}
        if cast:
            entries = []
            for edge in (cast.get("edges") or [])[:5]:
                node = edge.get("node") or {}
                name = (node.get("name") or {}).get("nameText") or {}
                name = name.get("text") or ""
                chars = [c.get("name") or "" for c in (node.get("characters") or [])]
                chars = [c for c in chars if c]
                if chars:
                    entries.append(f"{name} as {', '.join(chars)}")
                else:
                    entries.append(name)
            enrichment["topCast"] = ", ".join(entries)

        # Award counts
        wins = main.get("wins") or {}
        noms = main.get("nominationsExcludeWins") or {}
        enrichment["awardWins"] = wins.get("total") or 0
        enrichment["awardNominations"] = noms.get("total") or 0

        # Production budget
        budget = main.get("productionBudget") or {}
        if budget:
            b = budget.get("budget") or {}
            amt = b.get("amount")
            cur = b.get("currency") or "USD"
            if amt is not None:
                enrichment["budget"] = f"{cur} {amt:,}"

        # Box office (opening weekend, lifetime, worldwide)
        bg = main.get("openingWeekendGross") or {}
        if bg:
            total = (bg.get("gross") or {}).get("total") or {}
            amt = total.get("amount")
            cur = total.get("currency") or "USD"
            if amt is not None:
                enrichment["openingWeekendGross"] = f"{cur} {amt:,}"

        lg = main.get("lifetimeGross") or {}
        if lg:
            total = lg.get("total") or {}
            amt = total.get("amount")
            cur = total.get("currency") or "USD"
            if amt is not None:
                enrichment["lifetimeGross"] = f"{cur} {amt:,}"

        wg = main.get("worldwideGross") or {}
        if wg:
            total = wg.get("total") or {}
            amt = total.get("amount")
            cur = total.get("currency") or "USD"
            if amt is not None:
                enrichment["worldwideGross"] = f"{cur} {amt:,}"

        # Filming locations
        locs = main.get("filmingLocations") or {}
        enrichment["filmingLocations"] = ", ".join(
            e["node"]["text"] for e in (locs.get("edges") or [])
        )

        # Spoken languages
        langs = main.get("spokenLanguages") or {}
        enrichment["spokenLanguages"] = ", ".join(
            l["text"] for l in (langs.get("spokenLanguages") or [])
        )

        # Technical specifications
        tech = main.get("technicalSpecifications") or {}
        if tech:
            sound = tech.get("soundMixes") or {}
            items = sound.get("items") or []
            if items:
                enrichment["soundMix"] = ", ".join(s["text"] for s in items)
            aspect = tech.get("aspectRatios") or {}
            items = aspect.get("items") or []
            if items:
                enrichment["aspectRatio"] = ", ".join(a["aspectRatio"] for a in items)
            cols = tech.get("colorations") or {}
            items = cols.get("items") or []
            if items:
                enrichment["color"] = ", ".join(c["text"] for c in items)

    except Exception as e:
        print(f"    Warning: Could not enrich {url}: {e}")

    return enrichment


def enrich_items(items: list[dict], link_key: str = "link") -> list[dict]:
    """
    Enrich a list of title dicts by visiting each individual IMDb page.
    Rate-limited with a random 5-10s gap between requests.
    """
    if not items:
        return items

    driver = get_driver()
    try:
        for i, item in enumerate(items):
            url = item.get(link_key, "")
            if not url:
                continue
            print(f"  Enriching ({i+1}/{len(items)}): {item.get('name', url)}")
            enrichment = enrich_title_data(driver, url)
            item.update(enrichment)
            if i < len(items) - 1:
                delay = random.uniform(5, 10)
                print(f"    Waiting {delay:.1f}s...")
                time.sleep(delay)
    finally:
        driver.quit()

    return items


def fetch_popular_movies() -> list[dict]:
    """
    Fetch information about popular Movies from IMDb.

    Returns:
        list of dict: A list where each dictionary contains Movie information,
        such as the Movie's name, link, and rating.
    """
    print(
        f"Fetching Popular Movies {CURRENT_YEAR} from IMDb  ->", IMDB_POPULAR_MOVIES_URL
    )

    movie_data = []
    driver = get_driver()
    try:
        driver.get(IMDB_POPULAR_MOVIES_URL)
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        json_data = json.loads(soup.find("script", type="application/ld+json").text)
        for movie in json_data["itemListElement"]:
            movie_name = movie["item"]["name"]
            try:
                movie_rating = movie["item"]["aggregateRating"]["ratingValue"]
            except KeyError:
                movie_rating = 0
            try:
                movie_votes = movie["item"]["aggregateRating"]["ratingCount"]
            except KeyError:
                movie_votes = 0
            movie_link = movie["item"]["url"]
            movie_image = movie["item"].get("image", "")
            genres = movie["item"].get("genre", "")
            duration = movie["item"].get("duration", "")
            runtime = 0
            if duration:
                try:
                    parts = (
                        duration.replace("PT", "")
                        .replace("H", " ")
                        .replace("M", "")
                        .split()
                    )
                    if len(parts) == 2:
                        runtime = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 1 and "H" in duration:
                        runtime = int(parts[0]) * 60
                    elif len(parts) == 1 and "M" in duration:
                        runtime = int(parts[0])
                except:
                    pass
            movie_data.append(
                {
                    "name": movie_name,
                    "rating": movie_rating,
                    "votes": movie_votes,
                    "link": movie_link,
                    "image": movie_image,
                    "plot": movie["item"].get("description", ""),
                    "genres": genres,
                    "runtime": runtime,
                    "certificate": movie["item"].get("contentRating", ""),
                }
            )
    finally:
        driver.quit()

    print("  Enriching Popular Movies from individual pages...")
    movie_data = enrich_items(movie_data)
    return movie_data


def fetch_top_50_movies() -> list[dict]:
    """
    Fetch information about the Top 50 Movies of the current year from IMDb.

    Returns:
        list of dict: A list where each dictionary contains Movie information,
        such as the Movie's name and link.
    """
    print(
        f"Fetching Top 50 Movies {CURRENT_YEAR} from IMDb   ->", IMDB_MOVIES_SEARCH_URL
    )

    movie_data = []
    driver = get_driver()
    try:
        driver.get(IMDB_MOVIES_SEARCH_URL)
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        json_data = (
            json.loads(soup.find("script", id="__NEXT_DATA__").text)
            .get("props", {})
            .get("pageProps", {})
            .get("searchResults", {})
            .get("titleResults", {})
            .get("titleListItems")
        )
        for movie in json_data:
            release_year = movie.get("releaseYear", {})
            year = (
                release_year.get("year", "")
                if isinstance(release_year, dict)
                else release_year
            )

            release_date = movie.get("releaseDate", {})
            release_day = release_date.get("day", "")
            release_month = release_date.get("month", "")
            release_year_full = release_date.get("year", "")

            genres_raw = movie.get("genres", [])
            genres = ", ".join(genres_raw) if isinstance(genres_raw, list) else ""

            primary_image = movie.get("primaryImage", {})
            image_url = primary_image.get("url", "")
            image_caption = primary_image.get("caption", "")

            production_status = movie.get("productionStatus", {})
            current_stage = production_status.get("currentProductionStage", {})
            status = current_stage.get("text", "")

            movie_data.append(
                {
                    "name": movie.get("titleText", "")
                    or movie.get("originalTitleText", ""),
                    "link": IMDB_BASE_URL + "/title/" + movie["titleId"] + "/",
                    "rating": movie.get("ratingSummary", {}).get("aggregateRating", 0),
                    "votes": movie.get("ratingSummary", {}).get("voteCount", 0),
                    "year": year,
                    "releaseDate": f"{release_day}/{release_month}/{release_year_full}",
                    "genres": genres,
                    "runtime": movie.get("runtime", ""),
                    "plot": movie.get("plot", ""),
                    "image": image_url,
                    "imageCaption": image_caption,
                    "metascore": movie.get("metascore", ""),
                    "certificate": movie.get("certificate", ""),
                    "status": status,
                }
            )
    finally:
        driver.quit()

    print("  Enriching Top 50 Movies from individual pages...")
    movie_data = enrich_items(movie_data)
    return movie_data


def fetch_top_250_movies() -> list[dict]:
    """
    Fetch the Top 250 Movies from IMDb and return structured data.
    """
    print(f"Fetching Top 250 Movies from IMDb       ->", IMDB_TOP_250_MOVIES_URL)

    movie_data = []
    driver = get_driver()
    try:
        driver.get(IMDB_TOP_250_MOVIES_URL)
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        json_data = json.loads(
            soup.find("script", attrs={"type": "application/ld+json"}).text
        )

        for rank, movie in enumerate(json_data["itemListElement"], 1):
            item = movie["item"]
            duration = item.get("duration", "")
            runtime = 0
            if duration:
                try:
                    parts = (
                        duration.replace("PT", "")
                        .replace("H", " ")
                        .replace("M", "")
                        .split()
                    )
                    if len(parts) == 2:
                        runtime = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 1 and "H" in duration:
                        runtime = int(parts[0]) * 60
                    elif len(parts) == 1 and "M" in duration:
                        runtime = int(parts[0])
                except Exception:
                    pass

            genre = item.get("genre", "")
            if isinstance(genre, list):
                genre = ", ".join(genre)

            movie_data.append(
                {
                    "Rank": rank,
                    "name": item["name"],
                    "IMDb Rating": item.get("aggregateRating", {}).get(
                        "ratingValue", ""
                    ),
                    "link": item["url"],
                    "image": item.get("image", ""),
                    "plot": item.get("description", ""),
                    "genres": genre,
                    "runtime": runtime,
                    "certificate": item.get("contentRating", ""),
                }
            )
    finally:
        driver.quit()

    print("  Enriching Top 250 Movies from individual pages...")
    movie_data = enrich_items(movie_data)
    return movie_data


def fetch_popular_shows() -> list[dict]:
    """
    Fetch information about popular TV Shows from IMDb.

    Returns:
        list of dict: A list where each dictionary contains TV Show information,
        such as the TV Show's name, link, and rating.
    """
    print(f"Fetching Popular TV Show {CURRENT_YEAR} from IMDb ->", IMDB_POPULAR_TV_URL)

    show_data = []
    driver = get_driver()
    try:
        driver.get(IMDB_POPULAR_TV_URL)
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        json_data = json.loads(soup.find("script", type="application/ld+json").text)
        for show in json_data["itemListElement"]:
            show_name = show["item"]["name"]
            try:
                show_rating = show["item"]["aggregateRating"]["ratingValue"]
            except KeyError:
                show_rating = 0
            try:
                show_votes = show["item"]["aggregateRating"]["ratingCount"]
            except KeyError:
                show_votes = 0
            show_link = show["item"]["url"]
            show_image = show["item"].get("image", "")
            genres = show["item"].get("genre", "")
            duration = show["item"].get("duration", "")
            runtime = 0
            if duration:
                try:
                    parts = (
                        duration.replace("PT", "")
                        .replace("H", " ")
                        .replace("M", "")
                        .split()
                    )
                    if len(parts) == 2:
                        runtime = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 1 and "H" in duration:
                        runtime = int(parts[0]) * 60
                    elif len(parts) == 1 and "M" in duration:
                        runtime = int(parts[0])
                except:
                    pass
            show_data.append(
                {
                    "name": show_name,
                    "rating": show_rating,
                    "votes": show_votes,
                    "link": show_link,
                    "image": show_image,
                    "plot": show["item"].get("description", ""),
                    "genres": genres,
                    "runtime": runtime,
                    "certificate": show["item"].get("contentRating", ""),
                }
            )
    finally:
        driver.quit()

    print("  Enriching Popular Shows from individual pages...")
    show_data = enrich_items(show_data)
    return show_data


def fetch_top_50_shows() -> list[dict]:
    """
    Fetch information about the Top 50 Shows of the current year from IMDb.

    Returns:
        list of dict: A list where each dictionary contains TV Show information,
        such as the TV Show's name and link.
    """
    print(f"Fetching Top 50 shows {CURRENT_YEAR} from IMDb    ->", IMDB_TV_SEARCH_URL)

    show_data = []
    driver = get_driver()
    try:
        driver.get(IMDB_TV_SEARCH_URL)
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        json_data = (
            json.loads(soup.find("script", id="__NEXT_DATA__").text)
            .get("props", {})
            .get("pageProps", {})
            .get("searchResults", {})
            .get("titleResults", {})
            .get("titleListItems")
        )
        for show in json_data:
            release_year = show.get("releaseYear", {})
            year = (
                release_year.get("year", "")
                if isinstance(release_year, dict)
                else release_year
            )

            release_date = show.get("releaseDate", {})
            release_day = release_date.get("day", "")
            release_month = release_date.get("month", "")
            release_year_full = release_date.get("year", "")

            genres_raw = show.get("genres", [])
            genres = ", ".join(genres_raw) if isinstance(genres_raw, list) else ""

            primary_image = show.get("primaryImage", {})
            image_url = primary_image.get("url", "")
            image_caption = primary_image.get("caption", "")

            production_status = show.get("productionStatus", {})
            current_stage = production_status.get("currentProductionStage", {})
            status = current_stage.get("text", "")

            show_data.append(
                {
                    "name": show.get("titleText", "")
                    or show.get("originalTitleText", ""),
                    "link": IMDB_BASE_URL + "/title/" + show["titleId"] + "/",
                    "rating": show.get("ratingSummary", {}).get("aggregateRating", 0),
                    "votes": show.get("ratingSummary", {}).get("voteCount", 0),
                    "year": year,
                    "releaseDate": f"{release_day}/{release_month}/{release_year_full}",
                    "genres": genres,
                    "runtime": show.get("runtime", ""),
                    "plot": show.get("plot", ""),
                    "image": image_url,
                    "imageCaption": image_caption,
                    "metascore": show.get("metascore", ""),
                    "certificate": show.get("certificate", ""),
                    "status": status,
                }
            )
    finally:
        driver.quit()

    print("  Enriching Top 50 Shows from individual pages...")
    show_data = enrich_items(show_data)
    return show_data


def fetch_top_250_tv() -> list[dict]:
    """
    Fetch the Top 250 TV Shows from IMDb and return structured data.
    """
    print(f"Fetching Top 250 TV Shows from IMDb     ->", IMDB_TOP_250_TV_URL)

    show_data = []
    driver = get_driver()
    try:
        driver.get(IMDB_TOP_250_TV_URL)
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        json_data = json.loads(
            soup.find("script", attrs={"type": "application/ld+json"}).text
        )

        for rank, show in enumerate(json_data["itemListElement"], 1):
            item = show["item"]
            duration = item.get("duration", "")
            runtime = 0
            if duration:
                try:
                    parts = (
                        duration.replace("PT", "")
                        .replace("H", " ")
                        .replace("M", "")
                        .split()
                    )
                    if len(parts) == 2:
                        runtime = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 1 and "H" in duration:
                        runtime = int(parts[0]) * 60
                    elif len(parts) == 1 and "M" in duration:
                        runtime = int(parts[0])
                except Exception:
                    pass

            genre = item.get("genre", "")
            if isinstance(genre, list):
                genre = ", ".join(genre)

            show_data.append(
                {
                    "Rank": rank,
                    "name": item["name"],
                    "IMDb Rating": item.get("aggregateRating", {}).get(
                        "ratingValue", ""
                    ),
                    "link": item["url"],
                    "image": item.get("image", ""),
                    "plot": item.get("description", ""),
                    "genres": genre,
                    "runtime": runtime,
                    "certificate": item.get("contentRating", ""),
                }
            )
    finally:
        driver.quit()

    print("  Enriching Top 250 TV Shows from individual pages...")
    show_data = enrich_items(show_data)
    return show_data


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

    if not fetched_data:
        return

    keys = list(dict.fromkeys(k for d in fetched_data for k in d.keys()))
    header = ", ".join(keys)

    file = open(file_path, "w")
    file.write(header + "\n\n")
    file.close()

    file = open(file_path, "a")
    for item in fetched_data:
        values = [str(item.get(k, "")) for k in keys]
        file.write(", ".join(f'"{v}"' for v in values) + "\n")
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
    file.write(
        "**Popular Movies:** [CSV File](/data/popular/movies.csv), [JSON File](/data/popular/movies.json)\n\n"
    )
    file.write(
        "**Popular TV Shows:** [CSV File](/data/popular/shows.csv), [JSON File](/data/popular/shows.json)\n\n"
    )
    file.write("---\n\n")
    file.write("## IMDb Top 50 Movies List\n\n")

    for i, item in enumerate(fetched_data, 1):
        file.write(f"{i}. [{item['name']}]({item['link']})\n\n")

    file.close()


if __name__ == "__main__":
    print("/// IMDb Top 50 & 250 Movie/TV Show Data Scraper ///\n")
    print(f"Original Medium Post: {ORIGINAL_POST_URL}\n")

    print("\n--- 1. Top 50 Movies ---")
    fetched_movies = fetch_top_50_movies()
    print("  Saving Top 50 Movies to CSV...")
    save_to_csv(fetched_movies, "data/top50/movies.csv", "movies")
    print("  Saving Top 50 Movies to Markdown...")
    save_to_md(fetched_movies)
    print("  Done.")

    print("\n--- 2. Top 250 Movies ---")
    fetched_top250_movies = fetch_top_250_movies()
    print("  Saving Top 250 Movies to CSV...")
    save_to_csv(fetched_top250_movies, "data/top250/movies.csv", "movies")
    print("  Done.")

    print("\n--- 3. Top 50 TV Shows ---")
    fetched_shows = fetch_top_50_shows()
    print("  Saving Top 50 TV Shows to CSV...")
    save_to_csv(fetched_shows, "data/top50/shows.csv", "shows")
    print("  Done.")

    print("\n--- 4. Top 250 TV Shows ---")
    fetched_top250_shows = fetch_top_250_tv()
    print("  Saving Top 250 TV Shows to CSV...")
    save_to_csv(fetched_top250_shows, "data/top250/shows.csv", "shows")
    print("  Done.")

    print("\n--- 5. Popular Movies ---")
    fetched_popular_movies = fetch_popular_movies()
    print("  Saving Popular Movies to CSV...")
    save_to_csv(fetched_popular_movies, "data/popular/movies.csv", "movies")
    print("  Done.")

    print("\n--- 6. Popular TV Shows ---")
    fetched_popular_shows = fetch_popular_shows()
    print("  Saving Popular TV Shows to CSV...")
    save_to_csv(fetched_popular_shows, "data/popular/shows.csv", "shows")
    print("  Done.")

    if sys.version_info < (3, 10):
        print("\nPrinting Top 50 Movies (Python < 3.10 format):")
        print_top_50_movies(fetched_movies)

    print("\n/// Scraping Complete ///")
    print(f"Original Medium Post: {ORIGINAL_POST_URL}")
