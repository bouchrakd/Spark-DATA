# Spark-DATA — Real-time marketplace analytics with PySpark Structured Streaming

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=flat-square&logo=apachespark&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-2C5BB4?style=flat-square)

> **Team project (2 students)** — CY Tech, Computer Science engineering programme, 2026.
> Authors: Bouchra Zamoum ([@bouchrakd](https://github.com/bouchrakd)) and [@Hajarachour](https://github.com/Hajarachour).

A small end-to-end **streaming data pipeline** that simulates user activity on a second-hand marketplace (in the style of LeBonCoin), processes it in real time with **PySpark Structured Streaming**, and displays live statistics and an interaction graph in a **Streamlit dashboard**.

## Architecture

```
generateur.py ──► data/stream/*.json ──► streaming.py (PySpark) ──► output/stats/  ──┐
 (event generator)     (input stream)      (Structured Streaming)    output/graph/  ──┴─► dashboard.py (Streamlit)
```

1. **`generateur.py` — event generator**
   Continuously writes JSON events: timestamp, user, user city, product, product category, seller, action type (like / VOUT / purchase) and price.

2. **`streaming.py` — PySpark Structured Streaming job**
   - Reads the event stream with an explicit schema.
   - **Windowed statistics**: 1-minute sliding windows (30-second slide) with a 30-second watermark, grouped by action type → number of actions and total price volume.
   - **Graph edges**: builds a stream of user → product and seller → product relationships.
   - Writes both outputs as JSON with checkpointing (`output/stats`, `output/graph`).

3. **`dashboard.py` — Streamlit dashboard** (auto-refresh every 5 seconds)
   - Live KPIs: likes, VOUT, purchases and total volume (€).
   - Table of real-time interactions.
   - Dynamic **graph of users, products and sellers** drawn with NetworkX and Matplotlib.

4. **`rapport.pdf`** — project report.

## Run it

```bash
pip install pyspark streamlit streamlit-autorefresh pandas networkx matplotlib

python generateur.py          # terminal 1: generate events
python streaming.py           # terminal 2: start the Spark streaming job
streamlit run dashboard.py    # terminal 3: open the dashboard
```

## What this project covers

Stream processing · event-time windows and watermarks · schema definition · checkpointing · graph modelling of user interactions · real-time data visualisation.
