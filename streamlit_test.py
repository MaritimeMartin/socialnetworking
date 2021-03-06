import re

import streamlit as st
from streamlit_agraph import Config, agraph
from thefuzz import process

from datamodel import DB, DbEdge, DbNode

# TODO: Topic Container?
#   Mehrere Nodes zu einer Topic zusammenfügen. Wer die Node supported supported to Topic,
#   Wird als ein Punkt dargestellt.


def fuzzy_clean(s: str):
    node_names = [node.label for node in DbNode.all()]

    new_s = process.extractOne(s, node_names)
    if not new_s:
        return s

    print(f"{s} -> {new_s}")
    if new_s[1] > 80:
        return new_s[0]
    return s


HASHTAG_PATTERN = re.compile(r'^#[^ !@#$%^&*(),.?":{}|<>]*$')


def check_hashtag_regex(s: str) -> bool:
    res = HASHTAG_PATTERN.fullmatch(s)
    if not res:
        st.error(f"This is not a hashtag: {s}.\nTry to use only numbers and letters.")
        return False
    return True


def clean_tags(s: str) -> str:
    if s[0] != "#":
        s = f"#{s.lower()}"
    else:
        s = s.lower()
    if not check_hashtag_regex(s):
        return
    s = fuzzy_clean(s)
    return s


def commit_hashes(hash1, hash2):
    hash1 = clean_tags(hash1)
    hash2 = clean_tags(hash2)

    if hash1 == hash2 or (not hash1 or not hash2):
        return
    DbNode.create(hash1)
    DbNode.create(hash2)
    DB.commit()
    DbEdge.create(source=hash1, target=hash2)
    DB.commit()


def create_test_data():
    print("NEW TEST DATE")
    print("###############\n")
    test_data = [
        ("dataengineer", "startups"),
        ("berlin", "dataengineer"),
        ("berlin", "startups"),
        ("digitalproducts", "digitaltransformation"),
        ("digitalproducts", "#crypto"),
        ("#diGitAltransformation", "#crypto"),
        ("marketing", "advertising"),
        ("marketing", "berlin"),
        ("berlin", "beer"),
        ("dbu", "beer"),
        ("startup", "berlin"),
        ("crypto", "startup"),
        ("datascience", "dateengineering"),
        ("dataanalytics", "marketing"),
        ("learning", "DBU"),
        ("datascience", "pentest"),
        ("pentest", "cybersecurity"),
        ("cybersecurity", "dbu"),
        ("beer", "marekting"),
        ("career", "datascience"),
        ("career", "money"),
        ("crypto", "bitcoin"),
        ("startup", "bitcoin"),
        ("erfolg", "dbu"),
        ("dbu", "studium"),
        ("studium", "freunde"),
        ("freunde", "dbu"),
        ("dataegnineer", "databases"),
        ("python", "databases"),
        ("pentest", "databases"),
        ("socialmedia", "marketing"),
        ("advertising", "socialmedia"),
        ("abtesting", "advertising"),
        ("digitalproducts", "crypto"),
        ("crypto", "money"),
    ]
    DbNode.delete_all()

    for d in test_data:
        commit_hashes(d[0], d[1])


def delete_edge(selected_item):
    source, target = selected_item.split("|")
    DbEdge.delete(source, target)


def like_edge(selected_item):
    source, target = selected_item.split("|")
    DbEdge.create(source, target)


def enter_password(password):
    if password == st.secrets["ADMIN_PASS"]:
        st.session_state["is_admin"] = True


def test_click():
    st.info("WORKS")


if __name__ == "__main__":
    FONT_SIZE = 20

    if len(DbNode.all()) > 10:
        FONT_SIZE = 12

    NODE_CONFIG = {
        "labelProperty": "label",
        "fontSize": FONT_SIZE,
        "highlightFontSize": FONT_SIZE,
        "highlightFontWeight": "bold",
        "fontWeight": "bold",
        "labelPosition": "center",
        "opacity": 0.7
    }

    GRAPH_CONFIG = Config(
        width=1200,
        height=600,
        directed=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",  # or "blue"
        collapsible=True,
        node=NODE_CONFIG,
        link={"labelProperty": "label", "renderLabel": True},
        # **kwargs e.g. node_size=1000 or node_color="blue"
    )

    st.set_page_config(page_title="DBU Topic Graph", layout="wide")
    col1, col2 = st.columns([3, 1])

    with col1:
        agraph(
            nodes=DbNode.all_to_graph(),
            edges=DbEdge.all_to_graph(),
            config=GRAPH_CONFIG,
        )

    with col2:
        st.button("Refresh")

        st.markdown("### Erstelle neue Tags und Connections.")
        with st.expander("Erstellen", expanded=False):
            st.markdown(
                """
                Gebt zwei Tags ein.
                - Wenn es sie noch nicht gibt, werden zwei Nodes und eine Connections zwischen ihnen erstellt.
                - Wenn es noch keine Connection gibt, dann wird diese erstellt.
                - Gibt es die Connection oder Tags bereits, wird ihr Gewicht erhöht.
            """
            )

            hash1 = st.text_input("Erstes Tag:", key="hash1")
            hash2 = st.text_input("Zweites Tag:", key="hash2")

            st.button("Erstellen", on_click=commit_hashes, args=(hash1, hash2))

        st.markdown("### Like eine Connection oder ein Tag")
        st.markdown(
            """
            Like eine Connection oder ein Tag und ihre Wertigkeit wird um eins erhöht.

            """
        )
        with st.expander("Like Node", expanded=False):
            liked_node = st.selectbox(
                "Tag auswählen:",
                [n.label for n in DbNode.all()],
                key="like_node_select",
            )

            st.button(
                "Like", key="like_node", on_click=DbNode.create, args=(liked_node,)
            )

        with st.expander("Like Edge", expanded=False):

            liked_edge = st.selectbox(
                "Connection auswählen:",
                [f"{e.source.label}|{e.target.label}" for e in DbEdge.all()],
                key="like_edge_select",
            )

            st.button("Like", key="like_edge", on_click=like_edge, args=(liked_edge,))

        if st.session_state.get("is_admin", False):

            st.markdown("### Das sind nicht die Druiden, die ihr sucht...")

            with st.expander("DANGER ZONE", expanded=False):

                st.error("Nichts anfassen, das ist nur für mich!")

                st.button("Test Data", on_click=create_test_data)

                st.markdown("---")

                st.write("Delete Nodes here")
                node_label = st.selectbox(
                    "Select a node:", [n.label for n in DbNode.all()]
                )

                st.button(
                    "Delete",
                    key="delete_node",
                    on_click=DbNode.delete,
                    args=(node_label,),
                )
                st.markdown("---")

                st.write("Delete Edges here")
                edges = DbEdge.all()
                edge_label = st.selectbox(
                    "Select a edge:",
                    [f"{e.source.label}|{e.target.label}" for e in edges],
                )
                st.button(
                    "Delete",
                    key="delete_edge",
                    on_click=delete_edge,
                    args=(edge_label,),
                )
                st.markdown("---")

                st.write("Clean all nodes and edges.")
                st.button(
                    "Clean All",
                    key="clean_all",
                    on_click=DbNode.delete_all,
                )

                st.markdown("---")
                st.write("Download Data")
                with open("db_model.sqlite", "rb") as file:
                    st.download_button("Download", file, file_name="db_model.sqlite")

        else:
            password = st.text_input("Admin Functions:", type="password")

            st.button(
                "Enter", key="enter_admin", on_click=enter_password, args=(password,)
            )
