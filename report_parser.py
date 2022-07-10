import pandas as pd
import zipfile
from os.path import exists
import typing

def subject_parser(allowedCiks, use_cache = False) -> set[int]:
    if (use_cache and exists("cache\\subjects.csv")):
        print ("Using cache for subjects")
        return
    print ("Building subjects")
    subjects = pd.DataFrame()
    for year in range (2012, 2019):
        for q in range (1, 5):
            year_str = str(year)
            q_str = str(q)
            folder = zipfile.ZipFile(f"reports\\{year_str}q{q_str}.zip")
            file = folder.open("sub.txt")
            report = pd.read_csv(file, sep='\t', header='infer')
            report = report[report['cik'].isin(allowedCiks)]
            report = report[report['form'] == '10-K']
            subjects = subjects.append(report, ignore_index = True)
    subjects.to_csv('cache\\subjects.csv', index = False)
    print ("Finished subjects")
    return set(subjects["adsh"])

def tag_parser(use_cache = False) -> set[str]:
    if (use_cache and exists("cache\\tags.csv")):
        print("Using cache for tags")
        return

    print ("Building tags")
    tags = pd.DataFrame()
    for year in range(2012, 2019):
        for q in range(1, 5):
            year_str = str(year)
            q_str = str(q)
            folder = zipfile.ZipFile(f"reports\\{year_str}q{q_str}.zip")
            file = folder.open("tag.txt")
            report = pd.read_csv(file, sep='\t', header='infer')
            report = report[report["custom"] == 0]
            tags = tags.append(report, ignore_index=True)
    tags.to_csv('cache\\tags.csv', index = False)
    print ("Finished tags")
    return set(tags["tag"])

def num_parser(adshIds, tagIds, use_cache=False):
    if (use_cache and exists("cache\\nums.csv")):
        print("Using cache for nums")
        return

    print("Building nums")
    nums = pd.DataFrame()
    for year in range(2012, 2019):
        for q in range(1, 5):
            year_str = str(year)
            q_str = str(q)
            folder = zipfile.ZipFile(f"reports\\{year_str}q{q_str}.zip")
            file = folder.open("num.txt")
            report = pd.read_csv(file, sep='\t', header='infer')
            report = report[report["adsh"].isin(adshIds)]
            report = report[report["tag"].isin(tagIds)]
            nums = nums.append(report, ignore_index=True)
    nums.to_csv('cache\\nums.csv', index = False)
    print("Finished nums")

if __name__ ==  "__main__":
    allowedCiks = [320193, 789019]
    adshIds = subject_parser(allowedCiks, use_cache = False)
    tagIds = tag_parser(use_cache = False)
    num_parser(adshIds, tagIds, use_cache = False)
