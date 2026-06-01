import streamlit as st
from streamlit_autorefresh import st_autorefresh

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from pathlib import Path


# ======================================
# Configuration Streamlit
# ======================================

st.set_page_config(
    page_title="Dashboard LeBonCoin Streaming",
    layout="wide"
)

# Rafraîchissement automatique toutes les 5 secondes
st_autorefresh(interval=5000, key="refresh")


# ======================================
# Dossiers
# ======================================

STATS_DIR = Path("output/stats")
GRAPH_DIR = Path("output/graph")


# ======================================
# Lecture des fichiers JSON Spark
# ======================================

def read_json_folder(folder):
    files = list(folder.glob("part-*.json"))

    if not files:
        return pd.DataFrame()

    dfs = []

    for file in files:
        try:
            df = pd.read_json(file, lines=True)
            dfs.append(df)
        except Exception:
            pass

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


stats_df = read_json_folder(STATS_DIR)
graph_df = read_json_folder(GRAPH_DIR)


# ======================================
# Titre
# ======================================

st.title("📊 Dashboard LeBonCoin Streaming")


# ======================================
# Calcul statistiques
# ======================================

likes = 0
vout = 0
achats = 0
volume = 0

if not stats_df.empty:

    if "action_type" in stats_df.columns:

        likes = int(
            stats_df[
                stats_df["action_type"] == "AIME"
            ]["nombre_actions"].sum()
        )

        vout = int(
            stats_df[
                stats_df["action_type"] == "VOUT"
            ]["nombre_actions"].sum()
        )

        achats = int(
            stats_df[
                stats_df["action_type"] == "ACHAT"
            ]["nombre_actions"].sum()
        )

    if "volume_prix" in stats_df.columns:
        volume = round(
            stats_df["volume_prix"].sum(),
            2
        )


# ======================================
# Cartes statistiques
# ======================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👍 Likes", likes)

with col2:
    st.metric("🛒 VOUT", vout)

with col3:
    st.metric("💰 Achats", achats)

with col4:
    st.metric("💶 Volume total", f"{volume:,.2f} €")


# ======================================
# Tableau événements
# ======================================

st.divider()

st.subheader("📡 Interactions en temps réel")

if graph_df.empty:

    st.warning(
        "Aucune interaction reçue pour le moment."
    )

else:

    st.dataframe(
        graph_df.tail(20),
        use_container_width=True
    )


# ======================================
# Graphe
# ======================================

st.divider()

st.subheader("🕸️ Graphe des interactions")

if graph_df.empty:

    st.info(
        "Le graphe apparaîtra dès réception des données."
    )

else:

    G = nx.DiGraph()

    # On limite le graphe aux 40 dernières interactions pour qu'il reste lisible
    recent_edges = graph_df.tail(40)

    for _, row in recent_edges.iterrows():

        src = row.get("src")
        dst = row.get("dst")
        relation = row.get("relationship")

        if pd.notna(src) and pd.notna(dst):

            G.add_edge(
                src,
                dst,
                label=relation
            )

    # Couleurs selon le type de nœud demandé dans le sujet
    node_colors = []

    for node in G.nodes():

        node_str = str(node)

        if node_str.startswith("usr_"):
            node_colors.append("skyblue")      # Utilisateur

        elif node_str.startswith("prod_"):
            node_colors.append("lightgreen")   # Produit

        elif node_str.startswith("sel_"):
            node_colors.append("orange")       # Vendeur

        else:
            node_colors.append("lightgray")

    fig, ax = plt.subplots(
        figsize=(16, 10)
    )

    pos = nx.spring_layout(
        G,
        seed=42,
        k=1.5
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=node_colors,
        node_size=1300,
        edgecolors="black",
        linewidths=0.8,
        ax=ax
    )

    nx.draw_networkx_edges(
        G,
        pos,
        arrows=True,
        arrowstyle="->",
        arrowsize=15,
        width=1.2,
        ax=ax
    )

    nx.draw_networkx_labels(
        G,
        pos,
        font_size=8,
        font_weight="bold",
        ax=ax
    )

    edge_labels = nx.get_edge_attributes(
        G,
        "label"
    )

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=7,
        ax=ax
    )

    # Légende
    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Utilisateurs (U)",
            markerfacecolor="skyblue",
            markeredgecolor="black",
            markersize=12
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Produits (P)",
            markerfacecolor="lightgreen",
            markeredgecolor="black",
            markersize=12
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Vendeurs (S)",
            markerfacecolor="orange",
            markeredgecolor="black",
            markersize=12
        )
    ]

    ax.legend(
        handles=legend_elements,
        loc="upper left"
    )

    ax.set_title(
        "Graphe dynamique : Utilisateurs → Produits → Vendeurs"
    )

    ax.axis("off")

    st.pyplot(fig)


# ======================================
# Infos système
# ======================================

st.divider()

st.success(
    "Dashboard connecté à PySpark Streaming."
)

st.caption(
    "Rafraîchissement automatique toutes les 5 secondes."
)
