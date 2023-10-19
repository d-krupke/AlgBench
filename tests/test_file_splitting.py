import os
from algbench import Benchmark

def test_file_splitting():

    benchmark = Benchmark("./test_file_split_benchmark")

    # random data generation taken from https://stackoverflow.com/questions/16308989/
    def generate_one_mb_results(args): 
        offset = ord(b'A')
        rand_bytes = os.urandom(1024 * 1024)
        array = bytearray(rand_bytes)
        for i, bt in enumerate(array):
            array[i] = offset + bt % 26
        return {str(args["index"]) : bytes(array).decode()}
        
    for i in range(100):
        benchmark.add(generate_one_mb_results, {"index" : i})

    # Hardcoded for now. The file splits are hardcoded in nfs_json_list to be made at 30 MB. 
    # For the 100MB + some curly brackets and environments, this should produce 4 files. 
    assert len(os.listdir("./test_file_split_benchmark/results")) == 4 

    benchmark.delete()