import pandas as pd

# Load the DataFrame
df = pd.read_pickle("./network_analysis/network_output/graph_stats_df.pickle")

# Preview
#print(df.head())

# Inspect structure
#print(df.columns)
#print(df.shape)

# Look at cell nodes only
cell_df = df[df["node_type"] == "cell"]
#print(cell_df.head())

#print((cell_df.sort_values("betweenness_centrality", ascending=False).head(100)).to_string())

exclude = [
    r"\s*-\s*",
    r"[0-9]+.?[0-9]*",
]
combined_regex = '|'.join(exclude)
filtered_df = cell_df[~cell_df["node"].str.contains(combined_regex, regex=True, na=False)].sort_values(by="betweenness_centrality", ascending=False)

print(filtered_df.head(100).to_string())