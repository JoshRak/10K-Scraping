import pandas as pd
from pivottablejs import pivot_ui

master = pd.read_csv("cache\\master.csv", header="infer")
pivot_ui(master, rows = ["tag", "uom", "name", "report_year", "adsh", "value"], height = "700px", aggregatorName = "Sum")