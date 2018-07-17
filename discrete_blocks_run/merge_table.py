import pandas as pd
import glob
'''Takes all of the files in ./tables/ and merges them into a csv, removing the headers, and saves new csv'''

interesting_files = glob.glob("./tables/*.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)
df.to_csv("merged_blocks.csv")
