import json
import pandas as pd
import os
import re
import requests
from bs4 import BeautifulSoup


def parse_submission(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    if is_main_file(filepath.name):
        submissions_df = pd.DataFrame.from_dict(data["filings"]["recent"])
    else:
        submissions_df = pd.DataFrame.from_dict(data)

    submissions_df = submissions_df[submissions_df["form"]
                                    == '10-K'].reset_index()
    submissions_df["cik"] = filepath.name[3:13]
    submissions_df["filingDate"] = pd.to_datetime(
        submissions_df["filingDate"], format="%Y-%m-%d")
    submissions_df['xbrlDocument'] = submissions_df.apply(
        lambda x: get_xbrl_location(x['cik'], x['accessionNumber']), axis=1)

    submissions_df = submissions_df[["cik", "accessionNumber", "filingDate",
                                     "reportDate", "form", "primaryDocument", "isXBRL", "isInlineXBRL", "xbrlDocument"]]
    return submissions_df


def get_xbrl_location(cik, accessionNumber):
    accessionNumberRaw = accessionNumber.replace("-", "")
    url = f"https://sec.gov/Archives/edgar/data/{cik}/{accessionNumberRaw}/{accessionNumber}-index.html"

    headers = {
        'User-Agent': 'test',
        'From': 'youremail@domain.example'  # This is another valid field
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features="html.parser")
    # dataTable = soup.find("table", {"summary": "Data Files"})
    next = False
    for row in soup.findAll("td"):
        if (next):
            return row.text
        if "XBRL INSTANCE DOCUMENT" in str(row):
            next = True
    return ""


def parse_all(directory, allowedCiks):
    submissions_df = pd.DataFrame()
    for filepath in os.scandir(directory):
        if filepath.is_file() and any(cik in filepath.name for cik in allowedCiks):
            submissions_df = submissions_df.append(
                parse_submission(filepath), ignore_index=True)
    submissions_df.sort_values(
        by=["cik", "filingDate"], inplace=True, ignore_index=True)
    submissions_df.to_csv("submissions.csv")


def is_main_file(filename: str):
    return re.fullmatch(r"CIK\d{10}.json", filename)


if __name__ == "__main__":
    parse_all("submissions", ["0000320193", "0000789019"])
