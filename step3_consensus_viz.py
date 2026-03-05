import toytree
import toyplot.pdf
import json
import glob
import os

def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

def main():
    cfg = load_config()
    tree_dir = cfg['bootstrap_output_dir']
    consensus_dir = cfg['consensus_output_dir']  # Updated key
    os.makedirs(consensus_dir, exist_ok=True)    
    # Create the final output directory
    os.makedirs(consensus_dir, exist_ok=True)    

    tree_files = glob.glob(os.path.join(tree_dir, "tree_*.nwk"))
    if not tree_files:
        print(f"No trees found in {tree_dir}")
        return

    trees = [toytree.tree(f) for f in tree_files]
    mtree = toytree.mtree(trees)

    print(f"Analyzing {len(trees)} trees. Saving results to {consensus_dir}...")

    # Visualization: Cloud Tree
    canvas_cloud, axes_cloud, mark_cloud = mtree.draw_cloud_tree(fixed_order=True)
    toyplot.pdf.render(canvas_cloud, os.path.join(consensus_dir, "cloud_tree.pdf"))

    # Visualization: Consensus Tree
    consensus = mtree.get_consensus_tree()
    canvas_con, axes_con, mark_con = consensus.draw(ts='p')
    toyplot.pdf.render(canvas_con, os.path.join(consensus_dir, "consensus_tree.pdf"))

    # Data: Newick Consensus
    with open(os.path.join(consensus_dir, "final_consensus.nwk"), "w") as f:
        f.write(consensus.write())

    print(f"\nSuccess! Check the '{consensus_dir}' folder for your PDF and Newick files.")

if __name__ == "__main__":
    main()

