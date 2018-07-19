import pandas as pd
import glob
'''Takes all of the files in ./tables/ and merges them into a csv, removing the headers, and saves new csv'''

interesting_files = glob.glob("./tables/*.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)

percent_list = ["0.5", "0.1"]

for perc in percent_list:
    df["a/p^2 (b) " + perc] = (df["darea"]) / (df["dperim"] * df["dperim"])
    df["w_a/p^2 (b) " + perc] = (df["dparea"]) / (df["dpperim"] * df["dpperim"])
    df["rank_a/p^2 (b) " + perc] = df["a/p^2 (b) " + perc].rank()
    df["rank_w_a/p^2 (b) " + perc] = df["w_a/p^2 (b) " + perc].rank()

df = df.rename(columns={'dperim': 'perim (b)', 'dpperim': 'w_perim (b)', 
                        'darea': 'area (b)', 'dparea': 'w_area (b)'})

df.to_csv("merged_blocks.csv")


