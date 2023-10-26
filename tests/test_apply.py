import os
from algbench import Benchmark

def test_file_splitting():

    benchmark = Benchmark("./test_apply")

    def generate_entry(args): 
        return {str(args["index"]) : f"Data for entry {args["index"]}"}
        
    for i in range(200):
        benchmark.add(generate_entry, {"index" : i})

    # assert len(os.listdir("./test_file_split_benchmark/results")) == 4 

    # benchmark.delete()