import pandas as pd
import numpy as np
import lzma
import json
import os
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, to_tree

def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

def ncd(obj1, obj2, preset=6):
    s1, s2 = str(obj1).encode(), str(obj2).encode()
    c1 = len(lzma.compress(s1, preset=preset))
    c2 = len(lzma.compress(s2, preset=preset))
    c12 = len(lzma.compress(s1 + s2, preset=preset))
    return (c12 - min(c1, c2)) / max(c1, c2)

def get_newick(node, leaf_names):
    if node.is_leaf():
        return f"{leaf_names[node.id]}"
    return f"({get_newick(node.left, leaf_names)},{get_newick(node.right, leaf_names)})"

def generate_nj_tree(df, config):
    cols = df.columns
    n = len(cols)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = ncd(df.iloc[:, i].tolist(), 
                       df.iloc[:, j].tolist(), 
                       preset=config['compression_level'])
            dist_matrix[i, j] = dist_matrix[j, i] = dist
    
    Z = linkage(squareform(dist_matrix), method=config['method'])
    return get_newick(to_tree(Z), cols.tolist()) + ";"

def main():
    cfg = load_config()
    
    # Ensure directories exist
    os.makedirs(cfg['bootstrap_output_dir'], exist_ok=True)
    os.makedirs(cfg['consensus_output_dir'], exist_ok=True)
    
    try:
        df = pd.read_csv(cfg['input_csv'])
        if cfg['drop_na']:
            df = df.dropna()
        if cfg['verbose']:
            print(f"Loaded {cfg['input_csv']} with {len(df.columns)} columns.")
    except Exception as e:
        print(f"Error: {e}")
        return

    for i in range(cfg['bootstrap_iterations']):
        if cfg['verbose']:
            print(f"Generating Tree {i+1}/{cfg['bootstrap_iterations']}...")
            
        boot_df = df.sample(frac=1.0, replace=True)
        nwk = generate_nj_tree(boot_df, cfg)
        
        output_path = os.path.join(cfg['bootstrap_output_dir'], f"tree_{i}.nwk")
        with open(output_path, "w") as f:
            f.write(nwk)

    print(f"\nBootstrap trees saved to: {cfg['bootstrap_output_dir']}/")
    print(f"Ready for Step 3 consensus generation in: {cfg['consensus_output_dir']}/")

if __name__ == "__main__":
    main()

