from algbench import read_as_pandas

if __name__=="__main__":
    t = read_as_pandas("./03_benchmark_data/", lambda result: {"instance": result["parameters"]["args"]["instance_name"],
                                                       "strategy":  result["parameters"]["args"]["alg_params"]["strategy"],
                                                       "interchange": result["parameters"]["args"]["alg_params"].get("interchange", None),
                                                       "colors": result["data"]["result"]["n_colors"],
                                                       "runtime": result["data"]["runtime"]})
    t.to_json("./06_simplified_results.json.zip")
    