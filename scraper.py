
"""
goes and does "the work", scraping the
page and returning the two primary values.
"""

import json
import os
from random import choice
from bs4 import BeautifulSoup
from requests import get
from lib.headerparse import fromFile
get_data = lambda: json.loads(open("data.json", "r").read())

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
relative = lambda p: os.path.join(__location__, p)
open_relative = lambda f, t: open(relative(f), t)

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
    print("> response size:", len(soup.text))
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

def insider_changes(tickers):
    # print("relative")
    if not os.path.exists(os.path.join(__location__, "insider-cache.json")):
        open_relative("insider-cache.json", "w").write("{}")
    insider_cache = json.loads(open_relative("insider-cache.json", "r").read())
    alerts = []
    # print(insider_cache)
    for ticker in tickers:
        # make sure in cache
        if ticker not in insider_cache:
            first_time = True
            insider_cache[ticker] = []
        else:
            first_time = False
        # request the page, get all data
        page = get(f"http://openinsider.com/screener?s={ticker}&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1")
        text = page.text
        soup = BeautifulSoup(text, "html.parser")
        tables = soup.find_all("table", class_="tinytable")
        # make sure 1 table
        if len(tables) != 1:
            return print(f"> tables was empty for '{ticker}'")
        # make table, get rows
        table = tables[0]
        # headers
        headers = table.find("thead").find("tr").find_all("th")
        headers = [c.text.strip() for c in headers]
        headers = [c.replace("\xa0", " ") for c in headers]
        # rows / cols
        rows = table.find("tbody").find_all("tr")
        rows = [[c.text.strip() for c in row.find_all("td")] for row in rows]

        # we care about:
        # Filing Date, Ticker, Insider Name, Title, Trade Type, Price, Value
        i_headers = ["Filing Date", "Ticker", "Insider Name", "Title", "Trade Type", "Price", "Value"]
        i_headers = [headers.index(h) for h in i_headers]
        rows = [[row[idx] for idx in i_headers] for row in rows]

        # filter by prior seen alerts
        if first_time:
            rows_seen = [" ".join(row) for row in rows]
            insider_cache[ticker] = rows_seen
        else:
            rows_seen = insider_cache[ticker]
            for row in rows:
                string_row = " ".join(row) # string representation of row
                if string_row not in rows_seen: # if the string rep not in seen
                    filing_date, row_ticker, insider_name, title, trade_type, price, value = row
                    trade_move = "BROUGHT +++" if "Purchase" in trade_type else "SOLD ---"
                    # get the profane moment
                    profane = choice([
                        "BIG BALLSACK", "SACK QUEEN"
                    ]) if trade_move == "BROUGHT +++" else choice([
                        "DICK RIDER", "CUM SWALLOWER", "CUM REFUNDER"
                    ])
                    message = "(new) (<@135605387373051905>, <@305561661484433419>) "
                    message += f"**{row_ticker}** {insider_name} - {title} ({profane}) {trade_move} {row_ticker}, {value} @ {price} (({filing_date}))"
                    print(">", message)
                    insider_cache[ticker] = [string_row] + insider_cache[ticker]
                    alerts.append(message)
                else: # this string is in the mix, all good
                    pass
    open_relative("insider-cache.json", "w").write(json.dumps(insider_cache, indent=4))
    return alerts


if __name__ == "__main__":
    # print(work())
    # insider_changes(["UUUU"])
    pass
