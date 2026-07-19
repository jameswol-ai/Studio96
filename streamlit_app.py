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

# ---- TABS (simplified & reordered) ----
tab_labels = [
    "🧠 AI Brain",
    "🏛️ Architecture",
    "🏗️ Structure",
    "⚡ MEP",
    "🌍 GIS & Site",
    "💰 Cost",
    "🎨 Render",
    "🚀 Full Sim",
    "🏙️ RL City",
    "📈 City Learning",
    "🤝 Diplomacy",
    "⚔️ War",
    "🎭 Culture",
    "🌌 Consciousness",
    "🧬 Meta‑Evo"
]
tabs = st.tabs(tab_labels)

# =========================================================
# TAB 0: AI BRAIN
# =========================================================
with tabs[0]:
    st.header("🧠 AI Design Brain")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.session_state.intent_text = st.text_area(
            "Describe your building intent",
            value=st.session_state.intent_text,
            height=100,
            placeholder="e.g., A 5-storey mixed-use building with courtyard..."
        )
    with col2:
        st.session_state.site_area = st.number_input(
            "Site area (m²)",
            value=st.session_state.site_area,
            min_value=100.0
        )
        if st.button("Generate Concept", use_container_width=True):
            st.success(f"Concept generated for '{st.session_state.intent_text[:30]}...' ({st.session_state.site_area} m²)")

# =========================================================
# TAB 1: ARCHITECTURE (with gridlines)
# =========================================================
with tabs[1]:
    st.header("🏛️ Architecture Engine")
    st.subheader("Floor Plan Grid")
    col1, col2 = st.columns(2)
    with col1:
        grid_spacing = st.slider("Grid spacing (m)", 2.0, 10.0, 6.0)
    with col2:
        grid_extent = st.slider("Grid size (m)", 10, 60, 30)
    if st.button("Show Gridlines"):
        if MATPLOTLIB_AVAILABLE:
            fig, ax = plt.subplots()
            ax.set_aspect('equal')
            ax.set_xlim(0, grid_extent)
            ax.set_ylim(0, grid_extent)
            ax.set_xticks(np.arange(0, grid_extent + grid_spacing, grid_spacing))
            ax.set_yticks(np.arange(0, grid_extent + grid_spacing, grid_spacing))
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_xlabel("X (m)")
            ax.set_ylabel("Y (m)")
            ax.set_title("Architectural Grid")
            st.pyplot(fig)
        else:
            st.info("Matplotlib not installed – showing numerical grid")
            rows = int(grid_extent / grid_spacing)
            grid_data = [[f"({i*grid_spacing:.0f},{j*grid_spacing:.0f})" for j in range(rows)] for i in range(rows)]
            st.table(grid_data[:10])  # limit rows for readability

# =========================================================
# TAB 2: STRUCTURE (element types)
# =========================================================
with tabs[2]:
    st.header("🏗️ Structural Engine")
    st.subheader("Typical Structural Elements")
    elements = {
        "Columns": "Vertical load‑bearing members (concrete/steel)",
        "Beams": "Horizontal members spanning between columns",
        "Slabs": "Floor/roof plates (one‑way or two‑way)",
        "Foundation": "Spread footings, piles, or raft",
        "Shear Walls": "Lateral stability cores"
    }
    st.table(elements.items())
    st.subheader("Conceptual Section")
    if st.button("Generate Section View"):
        if MATPLOTLIB_AVAILABLE:
            fig, ax = plt.subplots()
            ax.bar(["Footing", "Column", "Beam", "Slab"], [2, 5, 3, 0.3], color=["brown", "gray", "orange", "lightblue"])
            ax.set_ylabel("Typical depth (m)")
            ax.set_title("Structural Depth Profile")
            st.pyplot(fig)
        else:
            st.bar_chart({"Footing": 2, "Column": 5, "Beam": 3, "Slab": 0.3})

# =========================================================
# TAB 3: MEP
# =========================================================
with tabs[3]:
    st.header("⚡ MEP Systems")
    mep_tab1, mep_tab2, mep_tab3 = st.tabs(["❄️ Mechanical", "💡 Electrical", "🚿 Plumbing"])
    with mep_tab1:
        st.metric("Cooling Load", f"{random.randint(80, 250)} kW")
        st.metric("Heating Load", f"{random.randint(50, 200)} kW")
        st.metric("Airflow", f"{random.randint(2000, 8000)} m³/h")
        st.write("Duct Sizing")
        w = st.slider("Duct Width (cm)", 20, 100, 40, key="mw")
        h = st.slider("Duct Height (cm)", 10, 50, 20, key="mh")
        st.write(f"Area: {w*h} cm²")
    with mep_tab2:
        col_a, col_b = st.columns(2)
        col_a.metric("Total Load", f"{random.randint(50, 500)} kVA")
        col_b.metric("LPD", f"{random.uniform(8, 15):.1f} W/m²")
        st.json({"Lights":"3x16A","Sockets":"6x20A","HVAC":"2x32A","Elevator":"1x63A"})
    with mep_tab3:
        st.metric("Daily Water", f"{random.randint(1000, 5000)} L")
        st.metric("Sewage Flow", f"{random.randint(800, 4000)} L/day")
        pipe = st.selectbox("Material", ["Copper","PVC","PEX"])
        diam = st.slider("Diameter (mm)", 15, 100, 25, key="pd")
        st.write(f"{pipe} Ø{diam}mm")

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
# TAB 5: COST
# =========================================================
with tabs[5]:
    st.header("💰 Cost Engine")
    area = st.number_input("Floor Area (m²)", value=500.0)
    st.metric("Estimated Cost", f"${area * random.randint(400, 1200):,.0f}")
    st.bar_chart({"Foundation": 15, "Structure": 30, "MEP": 25, "Finishes": 20, "Other": 10})

# =========================================================
# TAB 6: RENDER
# =========================================================
with tabs[6]:
    st.header("🎨 3D Massing")
    if MATPLOTLIB_AVAILABLE:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(*[np.random.rand(50) for _ in range(3)])
        st.pyplot(fig)
    else:
        st.warning("Matplotlib not installed – 3D disabled")

# =========================================================
# TAB 7: FULL SIMULATION
# =========================================================
with tabs[7]:
    st.header("🚀 Full Simulation")
    if st.button("Run All Modules"):
        steps = ["AI","Architecture","Structure","MEP","Cost","Render","Export"]
        p = st.progress(0)
        for i, s in enumerate(steps):
            st.write(s)
            time.sleep(0.2)
            p.progress((i+1)/len(steps))
        st.success("Simulation complete")

# =========================================================
# TAB 8: RL CITY
# =========================================================
with tabs[8]:
    st.header("🏙️ RL City")
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
    st.header("📈 Learning Curve")
    if rl_engine.history:
        st.line_chart(rl_engine.history)
    else:
        st.info("Run RL City first")

# =========================================================
# TAB 10: DIPLOMACY
# =========================================================
with tabs[10]:
    st.header("🤝 Diplomacy Network")
    nations = ["Alpha","Beta","Gamma","Delta","Epsilon"]
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
# TAB 11: WAR
# =========================================================
with tabs[11]:
    st.header("⚔️ War System")
    c1, c2 = st.columns(2)
    with c1: attacker = st.selectbox("Attacker", ["Alpha","Beta","Gamma"])
    with c2: defender = st.selectbox("Defender", ["Beta","Gamma","Delta"])
    if st.button("Simulate Battle"):
        st.metric("Outcome", random.choice(["Victory","Stalemate","Defeat"]))

# =========================================================
# TAB 12: CULTURE
# =========================================================
with tabs[12]:
    st.header("🎭 Culture System")
    cities = ["City A","City B","City C","City D"]
    st.bar_chart(dict(zip(cities, np.random.rand(4))))

# =========================================================
# TAB 13: CONSCIOUSNESS
# =========================================================
with tabs[13]:
    st.header("🌌 Civilization Consciousness")
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
    st.header("🧬 Meta‑Evolution View")
    st.info("Meta‑learning layer active (conceptual)")
