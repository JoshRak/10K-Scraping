from argparse import Namespace
from os import access
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import xml.etree.ElementTree as ET


def parse_all(startYear, endYear):
    submissions_df = pd.read_csv("submissions.csv")
    submissions_df["filingDate"] = pd.to_datetime(
        submissions_df["filingDate"], format="%Y-%m-%d")
    submissions_df["reportDate"] = pd.to_datetime(
        submissions_df["reportDate"], format="%Y-%m-%d")

    submissions_df = submissions_df[(
        submissions_df["reportDate"].dt.year >= startYear) & (submissions_df["reportDate"].dt.year <= endYear)]
    submissions_df.reset_index(inplace=True, drop=True)

    xbrl_df = pd.DataFrame(columns=["cik", "tag", "year", "unit", "value"])

    for i, row in submissions_df.iterrows():
        xbrl_df = xbrl_df.append(
            parse_report(row['cik'], row['accessionNumber'], row['xbrlDocument']))

    xbrl_df.to_csv("xbrl.csv", index=False)


def parse_report(cik, accessionNumber, xbrlDocument):
    xbrl_df = pd.DataFrame(columns=["cik", "tag", "year", "unit", "value"])
    data = get_xbrl(cik, accessionNumber, xbrlDocument)
    contexts = get_contexts(data)
    soup = BeautifulSoup(data, "xml")
    tags = soup.find_all()
    for tag in tags:
        if str(tag).startswith("<us-gaap") and tag.get("contextRef") in contexts:
            if check_int(tag.text):
                unit = tag.get("unitRef").lower()
                if "usd" in unit:
                    unit = "usd"
                if "shares" in unit:
                    unit = "shares"
                year = contexts[tag.get("contextRef")][0:4]
                xbrl_df = xbrl_df.append({"cik": cik,
                                          "tag": tag.name,
                                          "year": year,
                                          "unit": unit,
                                          "value": tag.text}, ignore_index=True)
    return xbrl_df


def check_int(s):
    if s == "":
        return False
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def get_contexts(data):
    contexts = {}
    soup = BeautifulSoup(data, "xml")
    tags = soup.find_all("context")
    for tag in tags:
        if tag.find("entity").find("segment") == None:
            if (tag.find("period").find("endDate") != None):
                date = tag.find("period").find("endDate").text
                contexts[tag.get("id")] = date
            else:
                date = tag.find("period").find("instant").text
                contexts[tag.get("id")] = date
    return contexts


def get_xbrl(cik, accessionNumber, xbrlDocument):
    accessionNumberRaw = accessionNumber.replace("-", "")
    url = f"https://sec.gov/Archives/edgar/data/{cik}/{accessionNumberRaw}/{xbrlDocument}"

    headers = {
        'User-Agent': 'test',
        'From': 'youremail@domain.example'
    }

    r = requests.get(url, headers=headers)
    return r.content


if __name__ == "__main__":
    parse_all(2012, 2018)
