import streamlit as st
import numpy as np
import time
import random
from collections import defaultdict

# ---- SAFE MATPLOTLIB ----
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# =====================================================
# IMPROVED RL CITY ENGINE (with decay & persistence)
# =====================================================
class CityPolicy:
    def __init__(self, lr=0.2, decay=0.99, max_size=1000):
        self.risk_map = defaultdict(float)
        self.lr = lr
        self.decay = decay
        self.max_size = max_size

    def choose_location(self, max_attempts=10):
        for _ in range(max_attempts):
            x, y = random.randint(0, 25), random.randint(0, 25)
            if self.risk_map[(x, y)] <= 2.0:
                return x, y
        # if still failing, return random anyways
        return random.randint(0, 25), random.randint(0, 25)

    def update(self, failed_nodes):
        for n in failed_nodes:
            x, y, z = n
            self.risk_map[(x, y)] += self.lr
        # decay all entries
        for k in list(self.risk_map.keys()):
            self.risk_map[k] *= self.decay
            if self.risk_map[k] < 0.01:
                del self.risk_map[k]
        # prune if too large
        if len(self.risk_map) > self.max_size:
            sorted_keys = sorted(self.risk_map, key=self.risk_map.get)
            for k in sorted_keys[:len(self.risk_map)-self.max_size]:
                del self.risk_map[k]

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
        if not nodes:
            return load
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

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================
if "intent_text" not in st.session_state:
    st.session_state.intent_text = ""
if "site_area" not in st.session_state:
    st.session_state.site_area = 1000.0
if "rl_engine" not in st.session_state:
    st.session_state.rl_engine = RLCityEngine()
if "active_tab" not in st.session_state:
    # read query param 'tab' to set default, else first tab
    query_params = st.query_params
    st.session_state.active_tab = query_params.get("tab", "AI Brain")

# =====================================================
# CACHED MATPLOTLIB FIGURES
# =====================================================
@st.cache_data
def grid_figure(grid_spacing, grid_extent):
    if not MATPLOTLIB_AVAILABLE:
        return None
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
    return fig

@st.cache_data
def structural_section_figure():
    if not MATPLOTLIB_AVAILABLE:
        return None
    fig, ax = plt.subplots()
    ax.bar(["Footing", "Column", "Beam", "Slab"], [2, 5, 3, 0.3],
           color=["brown", "gray", "orange", "lightblue"])
    ax.set_ylabel("Typical depth (m)")
    ax.set_title("Structural Depth Profile")
    return fig

@st.cache_data
def random_3d_scatter():
    if not MATPLOTLIB_AVAILABLE:
        return None
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(*[np.random.rand(50) for _ in range(3)])
    return fig

# =====================================================
# APP CONFIG
# =====================================================
st.set_page_config(page_title="Studio 96", layout="wide")
st.title("🏗️ Studio 96 — Unified Simulator")

# ---- TAB DEFINITION (radio buttons allow query param control) ----
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

# Active tab management
active_tab = st.radio("Navigate", tab_labels, index=tab_labels.index(st.session_state.active_tab) 
                       if st.session_state.active_tab in tab_labels else 0,
                       key="tab_radio", horizontal=True)
st.session_state.active_tab = active_tab

# =========================================================
# TAB CONTENT RENDERER
# =========================================================
if active_tab == "🧠 AI Brain":
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
            # Simulated AI: generates pseudo parameters from intent length
            floors = max(2, len(st.session_state.intent_text) % 20 + 3)
            grid = random.choice([6,8,10])
            st.session_state.generated = {
                "floors": floors,
                "grid_spacing": grid,
                "structural_system": random.choice(["RC Frame", "Steel", "Timber"]),
                "estimated_cost": floors * st.session_state.site_area * random.randint(800, 1200)
            }
            st.success(f"AI generated concept: {st.session_state.generated}")
            st.balloons()

elif active_tab == "🏛️ Architecture":
    st.header("🏛️ Architecture Engine")
    col1, col2 = st.columns(2)
    with col1:
        grid_spacing = st.slider("Grid spacing (m)", 2.0, 10.0, 6.0)
    with col2:
        grid_extent = st.slider("Grid size (m)", 10, 60, 30)
    if st.button("Show Gridlines"):
        if MATPLOTLIB_AVAILABLE:
            fig = grid_figure(grid_spacing, grid_extent)
            if fig:
                st.pyplot(fig)
        else:
            st.info("Matplotlib not installed – showing numerical grid")
            rows = int(grid_extent / grid_spacing)
            grid_data = [[f"({i*grid_spacing:.0f},{j*grid_spacing:.0f})" for j in range(rows)] for i in range(rows)]
            st.dataframe(grid_data[:10])  # limit display

elif active_tab == "🏗️ Structure":
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
            fig = structural_section_figure()
            if fig:
                st.pyplot(fig)
        else:
            st.bar_chart({"Footing": 2, "Column": 5, "Beam": 3, "Slab": 0.3})

elif active_tab == "⚡ MEP":
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

elif active_tab == "🌍 GIS & Site":
    st.header("🌍 Terrain Analysis")
    if MATPLOTLIB_AVAILABLE:
        x = np.linspace(0, 10, 100)
        fig, ax = plt.subplots()
        ax.plot(x, np.sin(x))
        st.pyplot(fig)
    else:
        st.line_chart(np.column_stack([np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100))]))

elif active_tab == "💰 Cost":
    st.header("💰 Cost Engine")
    area = st.number_input("Floor Area (m²)", value=500.0)
    cost = area * random.randint(400, 1200) if "generated" not in st.session_state else st.session_state.generated["estimated_cost"]
    st.metric("Estimated Cost", f"${cost:,.0f}")
    st.bar_chart({"Foundation": 15, "Structure": 30, "MEP": 25, "Finishes": 20, "Other": 10})

elif active_tab == "🎨 Render":
    st.header("🎨 3D Massing")
    if MATPLOTLIB_AVAILABLE:
        fig = random_3d_scatter()
        if fig:
            st.pyplot(fig)
    else:
        st.warning("Matplotlib not installed – 3D disabled")

elif active_tab == "🚀 Full Sim":
    st.header("🚀 Full Simulation")
    if st.button("Run All Modules"):
        steps = ["AI","Architecture","Structure","MEP","Cost","Render","Export"]
        p = st.progress(0)
        for i, s in enumerate(steps):
            st.write(s)
            time.sleep(0.2)
            p.progress((i+1)/len(steps))
        st.success("Simulation complete")

elif active_tab == "🏙️ RL City":
    st.header("🏙️ RL City")
    rl = st.session_state.rl_engine
    if st.button("Run City Step"):
        buildings, _, _, failed, stability, reward = rl.step()
        c1, c2, c3 = st.columns(3)
        c1.metric("Stability", round(stability, 3))
        c2.metric("Failures", len(failed))
        c3.metric("Reward", round(reward, 3))
        st.json(buildings)
    # show current risk heatmap (optional)
    if st.checkbox("Show Risk Map"):
        if rl.policy.risk_map:
            keys = list(rl.policy.risk_map.keys())
            vals = [rl.policy.risk_map[k] for k in keys]
            x_vals = [k[0] for k in keys]
            y_vals = [k[1] for k in keys]
            if MATPLOTLIB_AVAILABLE:
                fig, ax = plt.subplots()
                scatter = ax.scatter(x_vals, y_vals, c=vals, cmap="Reds", s=100)
                plt.colorbar(scatter, label="Risk")
                ax.set_title("Risk Heatmap")
                ax.set_xlim(0,25)
                ax.set_ylim(0,25)
                st.pyplot(fig)
            else:
                st.write("Enable Matplotlib for heatmap")

elif active_tab == "📈 City Learning":
    st.header("📈 Learning Curve")
    rl = st.session_state.rl_engine
    if rl.history:
        st.line_chart(rl.history)
    else:
        st.info("Run RL City steps first")

elif active_tab == "🤝 Diplomacy":
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

elif active_tab == "⚔️ War":
    st.header("⚔️ War System")
    c1, c2 = st.columns(2)
    with c1: attacker = st.selectbox("Attacker", ["Alpha","Beta","Gamma"])
    with c2: defender = st.selectbox("Defender", ["Beta","Gamma","Delta"])
    if st.button("Simulate Battle"):
        st.metric("Outcome", random.choice(["Victory","Stalemate","Defeat"]))

elif active_tab == "🎭 Culture":
    st.header("🎭 Culture System")
    cities = ["City A","City B","City C","City D"]
    st.bar_chart(dict(zip(cities, np.random.rand(4))))

elif active_tab == "🌌 Consciousness":
    st.header("🌌 Civilization Consciousness")
    state = np.random.rand(10)
    st.json({
        "stability": float(np.mean(state)),
        "conflict_pressure": float(np.std(state)),
        "innovation_drive": float(np.max(state))
    })

elif active_tab == "🧬 Meta‑Evo":
    st.header("🧬 Meta‑Evolution View")
    st.info("Meta‑learning layer active (conceptual)")
    if st.button("Run Meta Step"):
        st.json({"epoch": random.randint(1,100), "fitness": random.uniform(0.7,1.0)})

# ---- FOOTER ----
st.caption(f"Active tab: {st.session_state.active_tab}")