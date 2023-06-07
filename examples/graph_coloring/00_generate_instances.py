"""
Generate some graphs for our experiment.
It is important to save the instances so other people
can verify the results in the future.
"""

import os
import random

import networkx as nx
from _utils import InstanceDb

if __name__ == "__main__":
    assert not os.path.exists("01_instances.zip"), "Don't overwrite"
    instance_db = InstanceDb("01_instances.zip")
    for i in range(500):
        # Create a random graph
        n = random.randint(10, 300)
        p = 0.1 + 0.8 * random.random()  # [0.1-0.9]
        graph = nx.generators.random_graphs.erdos_renyi_graph(n, p)
        # save graph
        instance_name = f"graph_{i}"
        instance_db[instance_name] = graph
