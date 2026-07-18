# =========================================================
# 🏗️ RANDOM AI — UNIFIED CIVILIZATION SIMULATOR
# RL Cities + Culture + Diplomacy + War + Consciousness
# =========================================================

import streamlit as st
import numpy as np
import time
import random
import matplotlib.pyplot as plt
import sys
import os

# =========================================================
# PATH SETUP
# =========================================================
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.loader import load_pipelines
load_pipelines()

from core.registry import run_pipeline

# =========================================================
# 🧠 SESSION STATE
# =========================================================
if "result" not in st.session_state:
    st.session_state.result = None

if "intent_text" not in st.session_state:
    st.session_state.intent_text = ""

if "site_area" not in st.session_state:
    st.session_state.site_area = 1000.0

if "civil_history" not in st.session_state:
    st.session_state.civil_history = []


# =========================================================
# 🏙️ RL CITY ENGINE (CORE SIMULATION)
# =========================================================
class CityPolicy:
    def __init__(self):
        self.risk_map = {}
        self.lr = 0.2

    def choose_location(self):
        x, y = random.randint(0, 25), random.randint(0, 25)
        if self.risk_map.get((x, y), 0) > 2:
            return self.choose_location()
        return x, y

    def update(self, failed_nodes):
        for n in failed_nodes:
            x, y, z = n
            self.risk_map[(x, y)] = self.risk_map.get((x, y), 0) + self.lr


class RLBuildingEngine:
    def generate(self, policy):
        buildings = []
        for _ in range(5):
            x, y = policy.choose_location()
            buildings.append({
                "x": x,
                "y": y,
                "floors": random.randint(3, 10),
                "grid": random.choice([6, 8, 10, 12])
            })
        return buildings


class RLPhysics:
    def build_nodes(self, buildings):
        nodes = []
        for b in buildings:
            for z in range(b["floors"]):
                for x in range(0, b["grid"], 2):
                    for y in range(0, b["grid"], 2):
                        nodes.append((x + b["x"], y + b["y"], z))
        return nodes

    def loads(self, nodes):
        load = {n: 0.0 for n in nodes}
        max_z = max(n[2] for n in nodes)

        for n in nodes:
            if n[2] == max_z:
                load[n] += 1.0

        for _ in range(2):
            for (x, y, z), l in list(load.items()):
                below = (x, y, z - 1)
                if below in load:
                    load[below] += l * 0.7

        return load

    def collapse(self, load):
        return {n for n, l in load.items() if l > 2.0}


class RLCityEngine:
    def __init__(self):
        self.policy = CityPolicy()
        self.builder = RLBuildingEngine()
        self.physics = RLPhysics()
        self.history = []

    def step(self):
        buildings = self.builder.generate(self.policy)
        nodes = self.physics.build_nodes(buildings)
        loads = self.physics.loads(nodes)
        failed = self.physics.collapse(loads)

        self.policy.update(failed)

        stability = max(0, 1 - len(failed) / max(1, len(nodes)))
        reward = stability - 0.3 * len(failed)

        self.history.append(reward)

        return buildings, nodes, loads, failed, stability, reward


rl_engine = RLCityEngine()


# =========================================================
# 🧠 APP CONFIG
# =========================================================
st.set_page_config(page_title="Random AI Civilization Engine", layout="wide")

st.title("🏗️ Random AI — Civilization Engine (RL + Diplomacy + Consciousness)")


user_input = st.text_input("Input", "hello")

if st.button("Run Core Pipeline"):
    st.session_state.result = run_pipeline("main", user_input)
    st.success("Pipeline executed")


# =========================================================
# SIDEBAR — FULL CIVILIZATION STACK
# =========================================================
mode = st.sidebar.selectbox(
    "SYSTEM MODULE",
    [
        "AI Brain",
        "Architecture Generator",
        "Structure Engine",
        "MEP Systems",
        "GIS & Site",
        "Cost Engine",
        "Rendering",
        "Full Pipeline Simulation",

        # 🧠 CIVILIZATION LAYERS
        "🏙️ RL City",
        "🌆 City Learning",
        "🤝 Diplomacy Network",
        "⚔️ War System",
        "🎭 Culture System",
        "🧠 Civilization Consciousness",
        "🧬 Meta-Evolution View"
    ]
)


# =========================================================
# 🧠 AI BRAIN
# =========================================================
if mode == "AI Brain":

    st.header("🧠 Design Brain")

    st.session_state.intent_text = st.text_area(
        "Describe building intent",
        value=st.session_state.intent_text
    )

    st.session_state.site_area = st.number_input(
        "Site Area (m²)",
        value=st.session_state.site_area
    )

    if st.button("RUN FULL GENERATION"):
        try:
            st.session_state.result = run_pipeline(
                st.session_state.intent_text,
                st.session_state.site_area
            )
            st.success("Pipeline executed successfully")
        except Exception as e:
            st.error(str(e))

    if st.session_state.result:
        st.json(st.session_state.result)


# =========================================================
# 🏛️ ARCHITECTURE
# =========================================================
elif mode == "Architecture Generator":
    st.header("🏛️ Architecture Engine")
    floors = st.slider("Floors", 1, 50, 5)

    if st.button("Generate"):
        st.write([f"Floor {i}" for i in range(floors)])


# =========================================================
# 🧱 STRUCTURE
# =========================================================
elif mode == "Structure Engine":
    st.header("🏗️ Structural Check")
    st.info("Eurocode engine placeholder (external module)")


# =========================================================
# ⚡ MEP
# =========================================================
elif mode == "MEP Systems":
    st.header("MEP Systems")
    st.metric("HVAC Efficiency", f"{random.randint(70, 98)}%")


# =========================================================
# 🌍 GIS
# =========================================================
elif mode == "GIS & Site":
    st.header("Terrain Analysis")

    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    fig, ax = plt.subplots()
    ax.plot(x, y)

    st.pyplot(fig)


# =========================================================
# 💰 COST
# =========================================================
elif mode == "Cost Engine":
    st.header("Cost Engine")

    area = st.number_input("Area", value=500.0)
    st.metric("Cost", f"${area * random.randint(400, 1200):,.0f}")


# =========================================================
# 🧊 RENDERING
# =========================================================
elif mode == "Rendering":
    st.header("3D Massing")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(
        np.random.rand(50),
        np.random.rand(50),
        np.random.rand(50)
    )

    st.pyplot(fig)


# =========================================================
# 🚀 FULL PIPELINE
# =========================================================
elif mode == "Full Pipeline Simulation":
    st.header("System Simulation")

    steps = ["AI", "Architecture", "Structure", "MEP", "Cost", "Render", "Export"]
    p = st.progress(0)

    for i, s in enumerate(steps):
        st.write(s)
        time.sleep(0.2)
        p.progress((i + 1) / len(steps))

    st.success("Complete")


# =========================================================
# 🏙️ RL CITY MODULE (PHYSICS + RL)
# =========================================================
elif mode == "🏙️ RL City":

    st.header("🏙️ Reinforcement Learning City")

    if st.button("Run City Step"):

        buildings, nodes, loads, failed, stability, reward = rl_engine.step()

        c1, c2, c3 = st.columns(3)
        c1.metric("Stability", round(stability, 3))
        c2.metric("Failures", len(failed))
        c3.metric("Reward", round(reward, 3))

        st.json(buildings)


# =========================================================
# 🌆 LEARNING CURVE
# =========================================================
elif mode == "🌆 City Learning":

    st.header("Learning Curve")

    if rl_engine.history:
        st.line_chart(rl_engine.history)
    else:
        st.info("Run RL City first")


# =========================================================
# 🧠 CIVILIZATION CONSCIOUSNESS (SIMULATED VIEW)
# =========================================================
elif mode == "🧠 Civilization Consciousness":

    st.header("🌍 Global Civilization Mind")

    state = np.random.rand(10)

    mind = {
        "stability": float(np.mean(state)),
        "conflict_pressure": float(np.std(state)),
        "innovation_drive": float(np.max(state))
    }

    st.json(mind)


# =========================================================
# 🧬 META-EVOLUTION VIEW
# =========================================================
elif mode == "🧬 Meta-Evolution View":

    st.header("Evolution of Evolution")

    st.write("System is dynamically adjusting learning pressure, mutation rates, and stability constraints.")

    st.info("Meta-learning layer active (conceptual simulation)")
