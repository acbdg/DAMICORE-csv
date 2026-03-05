"DAMICORE for Python 3"
Summary of the Workflow

Spreadsheet (CSV): Loaded via pandas.

Bootstrap: df.sample(replace=True).

NCD: Custom logic using the lzma standard library (high efficiency).

Tree Inference: scipy.cluster.hierarchy converts distances to a tree structure.

Consensus: toytree.mtree generates the final visualization.


