"""
Building a graph out of hashtags
"""

from itertools import chain, combinations
from typing import List, Set, Tuple

from pyvis.network import Network

with open("hashes.csv", encoding="utf-8") as f:
    lines = f.readlines()

hash_tags = [line.strip() for line in lines]
net = Network(height="720", width="1280")


def flatten(tag_lines: List[str]) -> Tuple[Set[str], Set[str]]:
    """
    Flatten lines of Tags to edges and nodes.
    """
    splitted_tags = [tags.split(";") for tags in tag_lines]
    tag_edges = set(chain(*[list(combinations(a, 2)) for a in splitted_tags]))
    tag_nodes = set(chain(*splitted_tags))
    for t in tag_nodes:
        print(t)
    return tag_nodes, tag_edges


nodes, edges = flatten(hash_tags)
net.add_nodes(nodes)
for edge in edges:
    net.add_edge(*edge)

net.show_buttons(filter_=["physics"])
net.show("output.html")
