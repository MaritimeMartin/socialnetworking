from typing import List

from pony import orm
from streamlit_agraph import Edge, Node

DB = orm.Database()


class DbEdge(DB.Entity):

    value = orm.Required(int)
    source = orm.Required(lambda: DbNode, reverse="edges_sourcing")
    target = orm.Required(lambda: DbNode, reverse="edges_targeting")

    @classmethod
    @orm.db_session
    def exists(cls, source: str, target: str) -> bool:
        return orm.exists(
            e
            for e in cls
            if (e.source.label in (source, target))
            and (e.target.label in (source, target))
        )

    @classmethod
    @orm.db_session
    def create(cls, source, target, value=1):
        if not cls.exists(source, target):
            source_node = DbNode.find(source)
            target_node = DbNode.find(target)
            cls(source=source_node, target=target_node, value=value)
        else:
            edge = cls.find(source, target)
            try:
                edge.value += value
            except:
                print(f"source: {source}\ntarget: {target}\nedge: {edge}")

    @classmethod
    @orm.db_session
    def all(cls):
        return orm.select(e for e in cls).sort_by(lambda e: e.source.label)[:]

    @classmethod
    @orm.db_session
    def find(cls, source: str, target: str) -> "DbEdge":
        return orm.get(
            e
            for e in cls
            if ((e.source.label == source) and (e.target.label == target))
            or ((e.source.label == target) and (e.target.label == source))
        )

    @classmethod
    @orm.db_session
    def find_many(cls, source_or_target: str) -> List["DbEdge"]:
        return orm.select(
            e
            for e in cls
            if e.source.label == source_or_target or e.target.label == source_or_target
        )

    @classmethod
    @orm.db_session
    def delete(cls, source: str, target: str) -> None:
        orm.delete(
            e for e in cls if e.source.label == source and e.target.label == target
        )

    @classmethod
    def all_to_graph(cls):
        return [
            Edge(e.source.label, e.target.label, strokeWidth=e.value) for e in cls.all()
        ]


class DbNode(DB.Entity):

    label = orm.PrimaryKey(str)
    value = orm.Required(int, default=1)
    edges_sourcing = orm.Set(lambda: DbEdge, reverse="source", cascade_delete=True)
    edges_targeting = orm.Set(lambda: DbEdge, reverse="target", cascade_delete=True)

    @classmethod
    @orm.db_session
    def create(cls, label, value=1):
        if not orm.exists(n for n in cls if n.label == label):
            cls(label=label, value=value)
        else:
            node = cls.find(label)
            node.value += 1


    @classmethod
    @orm.db_session
    def all(cls):
        return orm.select(n for n in cls).sort_by(cls.label)[:]

    @classmethod
    @orm.db_session
    def find(cls, label):
        return orm.get(n for n in cls if n.label == label)

    @classmethod
    @orm.db_session
    def delete(cls, label):
        orm.delete(n for n in cls if n.label == label)

    @classmethod
    @orm.db_session
    def delete_all(cls):
        orm.delete(n for n in cls)

    @classmethod
    def all_to_graph(cls):
        return [Node(id=n.label, label=n.label, size=(n.value**1.5)*100) for n in cls.all()]


DB.bind(provider="sqlite", filename="db_model.sqlite", create_db=True)
DB.generate_mapping(create_tables=True)
