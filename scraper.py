
"""
goes and does "the work", scraping the
page and returning the two primary values.
"""

from bs4 import BeautifulSoup
from requests import get
from lib.headerparse import fromFile
get_data = lambda: json.loads(open("data.json", "r").read())

def work():
    page = get("https://www.aaii.com/sentimentsurvey/sent_results", headers=fromFile("headers/aaii.com.headers"))
    # print(page.text)
    soup = BeautifulSoup(page.text, "html.parser")
    headers = soup.find_all("header")
    if len(headers) == 0:
        print("> fatal error, page has restructured...")
        return "fatal", "error - page has restructured", {}
    rows = headers[0].find("table").find_all("tr")
    dates = {}
    latest_score = False
    latest_date = False
    for i, row in enumerate(rows):
        cols = row.find_all("td")
        cols = [c.text.strip().replace(":", "").replace("%", "") for c in cols]
        if cols[0] == "Reported Date" or len(cols) != 4: continue # ignore, this is main
        reported_date, bullish, neutral, bearish = cols # expand, casts
        score = float(bullish) - float(bearish)
        score = float("{:.2f}".format(score))
        if latest_score == False and latest_date == False:
            latest_score = score
            latest_date = reported_date
        dates[reported_date] = {
            "bullish": bullish,
            "bearish": bearish,
            "overall": score
        }
    return latest_date, latest_score, dates

def greed_index_score():
    page = get("https://alternative.me/crypto/fear-and-greed-index/", headers=fromFile("headers/gindex.headers"))
    soup = BeautifulSoup(page.text, "html.parser")
    greed_now_values = soup.find_all("div", class_="fng-value")
    if len(greed_now_values) == 4:
        greed_now = greed_now_values[0]
        greed_now = greed_now.find("div", class_="fng-circle")
        if greed_now == None and hasattr(greed_now, "text"):
            return False
        greed_now = greed_now.text
        return greed_now
    else:
        # error, run error fun
        return False


if __name__ == "__main__":
    print(work())
