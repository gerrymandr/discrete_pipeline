import pandas as pd
import glob
'''Takes all of the files in ./tables/ and merges them into a csv, removing the headers, and saves new csv'''

interesting_files = glob.glob("./tables/tigerline*tract.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)
df.to_csv("tigerline_tract.csv")

interesting_files = glob.glob("./tables/tigerline*bg.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)
df.to_csv("tigerline_bg.csv")

interesting_files = glob.glob("./tables/cb500k*tract.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)
df.to_csv("cb500k_tract.csv")

interesting_files = glob.glob("./tables/cb500k*bg.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)
df.to_csv("cb500k_bg.csv")

interesting_files = glob.glob("./tables/cb5m*tract.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)
df.to_csv("cb5m_tract.csv")

interesting_files = glob.glob("./tables/cb5m*bg.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)
df.to_csv("cb5m_bg.csv")

interesting_files = glob.glob("./tables/cb20m*tract.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)
df.to_csv("cb20m_tract.csv")

interesting_files = glob.glob("./tables/cb20m*bg.csv")
files = [pd.read_csv(f, header = 0, converters={'geoid': lambda x: str(x)}) for f in sorted(interesting_files)]
df = pd.concat(files, ignore_index = True)
df.to_csv("cb20m_bg.csv")
