# My agent: AutoFEA / MechCraft AI

**One-liner**: A conversational CAD and structural engineering agent that empowers non-technical users to design mechanical parts, run automated finite element analysis (FEA) and stress calculations in Python, view visual stress heatmaps, and generate downloadable CAD files.

---

### Tool Coverage Breakdown

* **Memory (Persistent Context)**:
  * Remembers engineering defaults & project constraints across user sessions:
    * Preferred unit system (Metric mm/N vs. Imperial in/lbf).
    * Standard engineering materials (6061-T6 Aluminum, Structural Steel, Carbon Fiber, PLA 3D Print).
    * Target Safety Factor threshold (e.g., minimum 2.0x required for safety).
    * Manufacturing process constraints (3D Printing vs. CNC Machining vs. Sheet Metal).

* **Function Tools**:
  1. `lookup_material_properties(material_name)`: Returns yield strength (MPa), Young's modulus (GPa), density (g/cm³), and Poisson's ratio.
  2. `calculate_beam_stress_and_deflection(load_N, length_mm, width_mm, height_mm, material)`: Runs bending moment, shear stress, max deflection (mm), and Factor of Safety (FoS) calculations.
  3. `generate_parametric_cad_file(part_type, dimensions)`: Generates 2D DXF or 3D STL CAD geometry programmatically via Python (`cadquery` / `ezdxf`).

* **Catalog / A2UI Displays**:
  * **Pass/Fail Engineering Report Card**: High-contrast A2UI status card showing **Factor of Safety (PASS/FAIL)**, Max Deflection, and Part Mass.
  * **Material Property Reference Cards**: Interactive cards comparing Yield Strength and Density across candidate materials.
  * **CAD File Download Card**: Card with direct links to download generated `.STL` and `.DXF` CAD geometry files.

* **Image Generation & Visualizations**:
  * **Matplotlib / Plotly Stress Heatmaps**: Generates 2D color-coded stress distribution plots (Von Mises stress heatmaps).
  * **Imagen 3 Renders**: Generates photorealistic 3D product concept renders and CAD assembly visualization images.

* **Code Sandbox (Python Compute)**:
  * Executes Python matrix calculations (`numpy` / `scipy`) to compute 2D beam element stiffness matrices, section moment of inertia tensors, and deflection under non-uniform loads.

---

### Implementation Configuration

* **Core Rails (Everyone)**: Memory, Function Tools, Evaluation, Deployment, Frontend
* **Stretch Menu (Pick Later)**: A2UI Pass/Fail Cards, Matplotlib Stress Heatmaps, Imagen 3 CAD Renders, Downloadable STL/DXF CAD exports.
* **First Eval Question**: *"Calculate the stress, maximum deflection, and safety factor for a 250mm long 6061-T6 Aluminum bracket carrying a 500N point load. If it fails safety factor 2.0x, automatically suggest the minimum required beam height."*
