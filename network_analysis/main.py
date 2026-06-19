import networkx as nx
import pandas as pd
import pickle
import json
import argparse
import random
import math
from pathlib import Path
from timeit import default_timer as timer


def get_source_target_nodes(G, mode):
    if mode == "all":
        return None
    elif mode == "cell_nodes":
        return [n for n, d in G.nodes(data=True) if d.get("type") == "cell"]
    elif mode == "attribute_nodes":
        return [n for n, d in G.nodes(data=True) if d.get("type") == "attr"]
    else:
        raise ValueError("Invalid source/target node mode")


def get_num_samples(G, sampling_percentage):
    n = G.number_of_nodes()
    k = math.ceil(n * sampling_percentage / 100)
    return max(1, min(k, n))


def compute_kadabra_bc(G, num_samples, source_nodes, seed):
    bc = nx.betweenness_centrality(
        G,
        k=num_samples,
        seed=seed,
        endpoints=False,
        normalized=True
    )
    if source_nodes is None:
        return bc
    return {n: bc[n] for n in source_nodes}


def compute_exact_bc(G, source_nodes):
    bc = nx.betweenness_centrality(
        G,
        normalized=True,
        endpoints=False
    )
    if source_nodes is None:
        return bc
    return {n: bc[n] for n in source_nodes}


def bc_in_k_neighborhood(G, nodes, radius):
    scores = {}
    for u in nodes:
        sub = nx.ego_graph(G, u, radius=radius)
        bc = nx.betweenness_centrality(sub, normalized=True)
        scores[u] = bc.get(u, 0.0)
    return scores


def main(args):
    start = timer()
    print("Loading graph...")
    G = pickle.load(open(args.graph, "rb"))
    print("Loaded graph in", timer() - start, "seconds")

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Basic statistics
    stats = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges()
    }

    # Determine source/target nodes
    source_nodes = get_source_target_nodes(G, args.betweenness_source_target_nodes)

    # Determine sample size
    if args.sampling_percentage:
        num_samples = get_num_samples(G, args.sampling_percentage)
    else:
        num_samples = args.num_samples

    # Compute BC
    df = pd.DataFrame()
    df["node"] = list(G.nodes())
    df["node_type"] = [G.nodes[n].get("type") for n in df["node"]]

    if args.betweenness_mode in ("exact", "all"):
        print("Computing exact BC...")
        start = timer()
        exact = compute_exact_bc(G, source_nodes)
        df["betweenness_centrality"] = df["node"].map(exact)
        stats["exact_bc_time"] = timer() - start

    if args.betweenness_mode in ("approximate", "all"):
        print("Computing approximate BC with", num_samples, "samples...")
        start = timer()
        approx = compute_kadabra_bc(G, num_samples, source_nodes, args.seed)
        df["approximate_betweenness_centrality"] = df["node"].map(approx)
        stats["approx_bc_time"] = timer() - start

    # Optional: BC in k-neighborhood
    if args.betweenness_in_k_neighborhood:
        min_r, max_r, step = args.betweenness_in_k_neighborhood
        for r in range(min_r, max_r + 1, step):
            print("Computing BC in radius", r)
            start = timer()
            scores = bc_in_k_neighborhood(G, df["node"], r)
            df[f"BC_at_radius_{r}"] = df["node"].map(scores)
            stats[f"bc_radius_{r}_time"] = timer() - start

    # Save outputs
    df.to_pickle(args.output_dir + "/graph_stats_df.pickle")
    with open(args.output_dir + "/statistics.json", "w") as f:
        json.dump(stats, f, indent=4)

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-g", "--graph", required=True)
    parser.add_argument("-o", "--output_dir", required=True)

    parser.add_argument("--betweenness_mode", default="approximate",
                        choices=["all", "exact", "approximate"])

    parser.add_argument("--betweenness_source_target_nodes",
                        default="all",
                        choices=["all", "cell_nodes", "attribute_nodes"])

    parser.add_argument("--num_samples", type=int)
    parser.add_argument("--sampling_percentage", type=float)

    parser.add_argument("--seed", type=int, default=42)

    parser.add_argument("--betweenness_in_k_neighborhood",
                        nargs=3, type=int)

    args = parser.parse_args()
    main(args)
