from zipfile import ZipFile, ZIP_LZMA
import networkx as nx
import json

class InstanceDb:
    """
    Simple helper to store and load the instances.
    Compressed zip to save disk space and making it small
    enough for git.
    """
    def __init__(self, path):
        self.path = path

    def __getitem__(self, name):
        with ZipFile(self.path, "r") as z:
            with z.open(name+".json", "r") as f:
                return nx.json_graph.node_link.node_link_graph(json.load(f))

    def __setitem__(self, name, graph):
        with ZipFile(self.path, compression=ZIP_LZMA, mode='a') as instance_archive:
            with instance_archive.open(name+".json", "w") as f:
                f.write(json.dumps(nx.json_graph.node_link.node_link_data(graph)).encode())

    def __iter__(self):
        with ZipFile(self.path, "r") as z:
            for f in z.filelist:
                yield f.filename[:-5]
