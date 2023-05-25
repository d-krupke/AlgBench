"""
This script simplifies the raw data to a small pandas table.
"""
from algbench import read_as_pandas

if __name__ == "__main__":
    t = read_as_pandas(
        "./03_benchmark_data/",
        lambda result: {
            "instance": result["parameters"]["args"]["instance_name"],
            "strategy": result["parameters"]["args"]["alg_params"]["strategy"],
            "interchange": result["parameters"]["args"]["alg_params"].get(
                "interchange", None
            ),
            "colors": result["result"]["n_colors"],
            "runtime": result["runtime"],
            "num_vertices": result["result"]["num_vertices"],
            "num_edges": result["result"]["num_edges"],
        },
    )
    t.to_json("./06_simplified_results.json.zip")
