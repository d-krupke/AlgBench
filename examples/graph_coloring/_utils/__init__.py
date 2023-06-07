import functools
import json
from zipfile import ZIP_LZMA, ZipFile

import networkx as nx


class InstanceDb:
    """
    Simple helper to store and load the instances.
    Compressed zip to save disk space and making it small
    enough for git.
    """

    def __init__(self, path):
        self.path = path

    @functools.lru_cache(10)
    def __getitem__(self, name):
        with ZipFile(self.path, "r") as z, z.open(name + ".json", "r") as f:
            return nx.json_graph.node_link.node_link_graph(json.load(f))

    def __setitem__(self, name, graph):
        self.__getitem__.cache_clear()
        with ZipFile(self.path, compression=ZIP_LZMA, mode="a") as instance_archive:
            with instance_archive.open(name + ".json", "w") as f:
                f.write(
                    json.dumps(nx.json_graph.node_link.node_link_data(graph)).encode()
                )

    def __iter__(self):
        with ZipFile(self.path, "r") as z:
            for f in z.filelist:
                yield f.filename[:-5]


# If you write a paper about your study, you want to use
# a uniform with for your plots. Find out, what the optimal
# width is and save it here to be shared for all notebooks.
PLOT_DOC_FULL_WIDTH = 10  # full width plot
PLOT_DOC_HALF_WIDTH = 4.5  # two plots in a row
