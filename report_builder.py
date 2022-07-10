import pandas as pd

def report_builder():
    subjects = pd.read_csv("cache\\subjects.csv", header='infer')
    nums = pd.read_csv("cache\\nums.csv", header = "infer")

    master = subjects.merge(nums, on = "adsh")

    master["report_date"] = pd.to_datetime(master["period"], format = "%Y%m%d")
    master["fact_date"] = pd.to_datetime(master["ddate"], format = "%Y%m%d")
    master['report_year'] = pd.DatetimeIndex(master['report_date']).year
    master['fact_year'] = pd.DatetimeIndex(master['fact_date']).year

    master = master[master["report_year"] == master["fact_year"]]

    cols = ["name", "report_year", "adsh", "tag", "uom", "value"]
    master = master[cols]

    master.to_csv("cache\\master.csv", index = False)

if __name__ == "__main__":
    report_builder()