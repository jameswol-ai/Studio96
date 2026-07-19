import streamlit as st
import numpy as np
import time
import random

# ---- SAFE MATPLOTLIB (prevents crash if not installed) ----
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ---- SESSION STATE ----
if "intent_text" not in st.session_state:
    st.session_state.intent_text = ""
if "site_area" not in st.session_state:
    st.session_state.site_area = 1000.0
if "civil_history" not in st.session_state:
    st.session_state.civil_history = []

# ---- RL CITY ENGINE ----
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

# ---- APP CONFIG ----
st.set_page_config(page_title="Studio 96", layout="wide")
st.title("🏗️ Studio 96 — Unified Simulator")

# ---- TABS (replaces sidebar) ----
tabs = st.tabs([
    "AI Brain",
    "Architecture",
    "Structure",
    "MEP",
    "GIS & Site",
    "Cost Engine",
    "Rendering",
    "Simulation",
    "RL City",
    "City Learning",
    "Diplomacy",
    "War System",
    "Culture",
    "Consciousness",
    "Meta-Evolution"
])

# =========================================================
# TAB 0: AI BRAIN
# =========================================================
with tabs[0]:
    st.header("🧠 Design Brain")
    st.session_state.intent_text = st.text_area(
        "Describe building intent",
        value=st.session_state.intent_text
    )
    st.session_state.site_area = st.number_input(
        "Site Area (m²)",
        value=st.session_state.site_area
    )
    if st.button("Generate Concept"):
        st.success(f"Concept generated for: '{st.session_state.intent_text}' ({st.session_state.site_area} m²)")

# =========================================================
# TAB 1: ARCHITECTURE
# =========================================================
with tabs[1]:
    st.header("🏛️ Architecture Engine")
    floors = st.slider("Floors", 1, 50, 5)
    if st.button("Generate Floor Plan"):
        st.write([f"Floor {i}" for i in range(floors)])

# =========================================================
# TAB 2: STRUCTURE
# =========================================================
with tabs[2]:
    st.header("🏗️ Structural Check")
    st.info("Eurocode engine placeholder (external module)")
    if st.button("Run Analysis"):
        st.metric("Capacity Ratio", f"{random.uniform(0.4, 0.95):.2f}")

# =========================================================
# TAB 3: MEP (Mechanical, Electrical, Plumbing)
# =========================================================
with tabs[3]:
    st.header("⚡ MEP Systems")
    mep_tab1, mep_tab2, mep_tab3 = st.tabs(["Mechanical", "Electrical", "Plumbing"])

    with mep_tab1:
        st.subheader("❄️ Mechanical (HVAC)")
        st.metric("Cooling Load", f"{random.randint(80, 250)} kW")
        st.metric("Heating Load", f"{random.randint(50, 200)} kW")
        st.metric("Airflow", f"{random.randint(2000, 8000)} m³/h")
        # Simple duct sizing
        st.write("Duct Size Suggestion")
        width = st.slider("Duct Width (cm)", 20, 100, 40)
        height = st.slider("Duct Height (cm)", 10, 50, 20)
        st.write(f"Cross-sectional area: {width * height} cm²")

    with mep_tab2:
        st.subheader("💡 Electrical")
        col1, col2 = st.columns(2)
        col1.metric("Total Connected Load", f"{random.randint(50, 500)} kVA")
        col2.metric("Lighting Power Density", f"{random.uniform(8, 15):.1f} W/m²")
        st.write("Circuit Schedule")
        circuits = {"Lights": "3x16A", "Sockets": "6x20A", "HVAC": "2x32A", "Elevator": "1x63A"}
        st.json(circuits)

    with mep_tab3:
        st.subheader("🚿 Plumbing")
        st.metric("Daily Water Demand", f"{random.randint(1000, 5000)} L")
        st.metric("Sewage Flow", f"{random.randint(800, 4000)} L/day")
        st.write("Pipe Sizing")
        pipe_type = st.selectbox("Pipe Material", ["Copper", "PVC", "PEX"])
        diameter = st.slider("Diameter (mm)", 15, 100, 25)
        st.write(f"Selected: {pipe_type} pipe, Ø{diameter}mm")

# =========================================================
# TAB 4: GIS & SITE
# =========================================================
with tabs[4]:
    st.header("🌍 Terrain Analysis")
    if MATPLOTLIB_AVAILABLE:
        x = np.linspace(0, 10, 100)
        fig, ax = plt.subplots()
        ax.plot(x, np.sin(x))
        st.pyplot(fig)
    else:
        st.line_chart(np.column_stack([np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100))]))

# =========================================================
# TAB 5: COST ENGINE
# =========================================================
with tabs[5]:
    st.header("💰 Cost Engine")
    area = st.number_input("Floor Area (m²)", value=500.0)
    st.metric("Estimated Cost", f"${area * random.randint(400, 1200):,.0f}")
    st.bar_chart({"Foundation": 15, "Structure": 30, "MEP": 25, "Finishes": 20, "Other": 10})

# =========================================================
# TAB 6: RENDERING
# =========================================================
with tabs[6]:
    st.header("3D Massing")
    if MATPLOTLIB_AVAILABLE:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(*[np.random.rand(50) for _ in range(3)])
        st.pyplot(fig)
    else:
        st.warning("Matplotlib not installed – 3D rendering disabled.")

# =========================================================
# TAB 7: FULL SIMULATION (pipeline)
# =========================================================
with tabs[7]:
    st.header("System Simulation")
    steps = ["AI Concept", "Architecture", "Structure", "MEP", "Cost", "Render", "Export"]
    p = st.progress(0)
    for i, s in enumerate(steps):
        st.write(s)
        time.sleep(0.2)
        p.progress((i + 1) / len(steps))
    st.success("Complete")

# =========================================================
# TAB 8: RL CITY
# =========================================================
with tabs[8]:
    st.header("🏙️ Reinforcement Learning City")
    if st.button("Run City Step"):
        buildings, _, _, failed, stability, reward = rl_engine.step()
        c1, c2, c3 = st.columns(3)
        c1.metric("Stability", round(stability, 3))
        c2.metric("Failures", len(failed))
        c3.metric("Reward", round(reward, 3))
        st.json(buildings)

# =========================================================
# TAB 9: CITY LEARNING
# =========================================================
with tabs[9]:
    st.header("Learning Curve")
    if rl_engine.history:
        st.line_chart(rl_engine.history)
    else:
        st.info("Run RL City first")

# =========================================================
# TAB 10: DIPLOMACY
# =========================================================
with tabs[10]:
    st.header("🤝 Diplomacy Network")
    nations = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    matrix = np.random.rand(len(nations), len(nations))
    if MATPLOTLIB_AVAILABLE:
        fig, ax = plt.subplots()
        cax = ax.matshow(matrix, cmap="coolwarm")
        fig.colorbar(cax)
        ax.set_xticks(range(len(nations)))
        ax.set_yticks(range(len(nations)))
        ax.set_xticklabels(nations)
        ax.set_yticklabels(nations)
        st.pyplot(fig)
    else:
        st.dataframe(matrix, columns=nations)

# =========================================================
# TAB 11: WAR SYSTEM
# =========================================================
with tabs[11]:
    st.header("⚔️ War System")
    col1, col2 = st.columns(2)
    with col1:
        attacker = st.selectbox("Attacker", ["Alpha", "Beta", "Gamma"])
    with col2:
        defender = st.selectbox("Defender", ["Beta", "Gamma", "Delta"])
    if st.button("Simulate Battle"):
        st.metric("Outcome", random.choice(["Victory", "Stalemate", "Defeat"]))

# =========================================================
# TAB 12: CULTURE SYSTEM
# =========================================================
with tabs[12]:
    st.header("🎭 Culture System")
    cities = ["City A", "City B", "City C", "City D"]
    st.bar_chart(dict(zip(cities, np.random.rand(4))))

# =========================================================
# TAB 13: CIVILIZATION CONSCIOUSNESS
# =========================================================
with tabs[13]:
    st.header("🌍 Global Civilization Mind")
    state = np.random.rand(10)
    st.json({
        "stability": float(np.mean(state)),
        "conflict_pressure": float(np.std(state)),
        "innovation_drive": float(np.max(state))
    })

# =========================================================
# TAB 14: META-EVOLUTION
# =========================================================
with tabs[14]:
    st.header("Evolution of Evolution")
    st.info("Meta-learning layer active (conceptual simulation)")
