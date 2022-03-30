from pprint import pprint

from datamodel import DbEdge, DbNode
from streamlit_agraph import Edge, Node

DbNode.create("test_label")

pprint(DbNode.all())
