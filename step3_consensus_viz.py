import os
import sys
import json
import glob
import toytree
import toyplot.pdf
from pathlib import Path


def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

def multiple_trees():
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

    return(mtree, consensus_dir)


def print_consensus(mtree, consensus_dir):
    # Define styles to generate
    # 'c' = curved, 'p' = phylogeny (straight/rectangular)i
    # ts - tree style
    # edge_type - line geometry
    # layout - tree orientation
    styles = [
        {"name": "curved", "stype": "c"},   
        {"name": "straight", "stype": "d"}
    ]

    for style in styles:
        suffix = style["name"]
        stype = style["stype"]
        
        print(f"Drawing {suffix} trees...")

        # 1. Cloud Tree
        canvas_cloud, axes_cloud, mark_cloud = mtree.draw_cloud_tree(
            ts='p',
            layout=stype,
            #edge_type=stype,
            fixed_order=True,
            width=700,
            height=700,
            node_labels="support",
            node_labels_style={"font-size": "8px", "fill": "red"}
        )
        toyplot.pdf.render(canvas_cloud, os.path.join(consensus_dir, f"cloud_tree_{suffix}.pdf"))

        # 2. Consensus Tree
        consensus = mtree.get_consensus_tree()
        canvas_con, axes_con, mark_con = consensus.draw(
            ts='p',
            layout=stype,
            #edge_type=stype,
            node_labels="support",
            node_labels_style={"font-size": "9px", "fill": "red"},
            width=800,
            height=800
        )
        toyplot.pdf.render(canvas_con, os.path.join(consensus_dir, f"consensus_tree_{suffix}.pdf"))

    # 3. Save Newick (only once as geometry doesn't affect the data)
    with open(os.path.join(consensus_dir, "final_consensus.nwk"), "w") as f:
        f.write(consensus.write())

    print(f"\n✅ Success! Saved 4 PDFs to: {consensus_dir}")

if __name__ == "__main__":

    mtree, consensus_dir = multiple_trees()

    # 1. Resolve workspace from our 'relay' file
    #try:
    #    if Path("folder.txt").exists():
    #        base_workspace = Path("folder.txt").read_text().strip()
    #        target_dir = os.path.join(base_workspace, "consensus_viz")
    #    else:
    #        target_dir = "output_results/consensus_viz"
    #except Exception:
    #    target_dir = "output_results/consensus_viz"

    ## 2. Ensure directory exists
    #os.makedirs(target_dir, exist_ok=True)

    # 3. Print consensus and cloud trees
    print_consensus(mtree, consensus_dir)

