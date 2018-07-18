import math
import pandas as pd
import glob
'''Takes all of the files in ./tables/ and merges them into a csv, removing the headers, and saves new csv'''

unit_name = ["tract", "bg"]
district_files = ["tigerline", "cb500k", "cb5m", "cb20m"]

for unit in unit_name:
    for shape in district_files:
        interesting_files = glob.glob("./tables/" + shape + "*" + unit + ".csv")
        files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
        df = pd.concat(files, ignore_index = True)

        # to add continuous polsby popper:
        df["cpolsbypop"] = (4 * math.pi * df["carea"]) / (df["cperim"] * df["cperim"])
        df = df[['geoid', 'carea', 'cperim', 'cpolsbypop', 'dperim_0.5', 'dpperim_0.5', 'dperim_pro_0.5', 'dpperim_pro_0.5', 'darea_0.5', 'dparea_0.5', 'darea_pro_0.5', 'dparea_pro_0.5', 'dperim_0.1', 'dpperim_0.1', 'dperim_pro_0.1', 'dpperim_pro_0.1', 'darea_0.1', 'dparea_0.1', 'darea_pro_0.1', 'dparea_pro_0.1']]
        df.to_csv("./tables_merged/" + shape + "_" + unit + ".csv")

