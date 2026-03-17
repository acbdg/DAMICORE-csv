import pandas as pd
import numpy as np
import lzma
import toytree
import json
import os
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, to_tree
import concurrent.futures
import multiprocessing
from tqdm import tqdm


# --- Configuration Loader ---
def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

# --- NCD & Tree Logic ---
def ncd(obj1, obj2, preset=6):
    """Calculates NCD using LZMA with configurable compression level."""
    s1, s2 = str(obj1).encode(), str(obj2).encode()
    # Use preset from config for fine-tuning speed vs accuracy
    c1 = len(lzma.compress(s1, preset=preset))
    c2 = len(lzma.compress(s2, preset=preset))
    c12 = len(lzma.compress(s1 + s2, preset=preset))
    return (c12 - min(c1, c2)) / max(c1, c2)

def get_newick(node, leaf_names):
    """Recursive helper to build Newick string from Scipy ClusterNode."""
    if node.is_leaf():
        return f"{leaf_names[node.id]}"
    return f"({get_newick(node.left, leaf_names)},{get_newick(node.right, leaf_names)})"

def generate_nj_tree(df, config):
    """Computes NCD matrix and clusters it using the method from config."""
    cols = df.columns
    n = len(cols)
    dist_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = ncd(df.iloc[:, i].tolist(), 
                       df.iloc[:, j].tolist(), 
                       preset=config['compression_level'])
            dist_matrix[i, j] = dist_matrix[j, i] = dist
    
    # Use the 'method' (e.g., 'average') defined in config.json
    Z = linkage(squareform(dist_matrix), method=config['method'])
    return get_newick(to_tree(Z), cols.tolist()) + ";"


def run_single_bootstrap(i, df, cfg):
    """Function executed by each worker core"""
    # 1. Sample with replacement
    boot_df = df.sample(frac=1.0, replace=True)
    
    # 2. Generate tree (Assuming this function is defined in your script)
    nwk = generate_nj_tree(boot_df, cfg)

    # 3. Save the tree
    file_name = f"tree_{i}.nwk"
    output_path = os.path.join(cfg['bootstrap_output_dir'], file_name)
    with open(output_path, "w") as f:
        f.write(nwk)
    
    return f"✅ Tree {i} saved."


# --- Execution ---
def main():
    # 1. Load Parameters
    cfg = load_config()
    
    # 2. Setup Directories
    os.makedirs(cfg['bootstrap_output_dir'], exist_ok=True)
    os.makedirs(cfg['consensus_output_dir'], exist_ok=True)

    # 3. Load and Clean Data
    if cfg['verbose']:
        print(f"Loading data")
    try:
        df = pd.read_csv(cfg['input_csv'], low_memory=False)
        if cfg['drop_na']:
            df = df.dropna()
        
        if cfg['verbose']:
            print(f"Successfully loaded {cfg['input_csv']} with {len(df.columns)} columns.")
    except Exception as e:
        print(f"Critical Error loading CSV: {e}")
        return

    # 4. Bootstrap Loop
    n_boots = cfg['bootstrap_iterations']
    if cfg['verbose']:
        print(f"Generating {n_boots} trees in '{cfg['bootstrap_output_dir']}'...")
        print(f"🚀 Starting parallel bootstrap on M1...")    

        # Using 6 workers is ideal for 16GB RAM to avoid swapping
        # while leaving 2 cores for system tasks.
        with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
        # We use a list comprehension to submit all jobs
        # mapping the range(n_boots) to our function
            futures = [executor.submit(run_single_bootstrap, i, df, cfg) for i in range(n_boots)]
        
        # Monitor progress as they finish
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    # Optional: print(result) to see progress
                except Exception as e:
                    print(f"❌ Bootstrapping failed for an iteration: {e}")

        if cfg['verbose']:
            print(f"[{i+1}/{n_boots}] Saved {file_name}")

    print("🏁 All bootstrap trees generated.")
    print(f"\nPhase 1 Complete. Raw trees are ready for Step 2 (Consensus).")

if __name__ == "__main__":
    main()

