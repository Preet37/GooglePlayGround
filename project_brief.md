# My agent: CircuitCraft AI

**One-liner**: A conversational hardware engineering assistant that translates plain-English project requirements into complete electronic circuit designs, component selections, parametric calculations, pinouts, and visual PCB concept renders.

---

### Tool Coverage Breakdown

* **Memory (Persistent Context)**:
  * Remembers platform & design constraints across user sessions:
    * Preferred microcontrollers (e.g., ESP32, Raspberry Pi Pico, Arduino Nano).
    * Logic voltage standard (3.3V vs. 5V).
    * Package type preference (Surface-Mount SMD vs. Through-Hole DIP).
    * Max current & power budget constraints (e.g., battery-powered vs. USB 5V).

* **Function Tools**:
  1. `search_components(query, category)`: Queries parametric component specs (microcontrollers, sensors, MOSFETs, op-amps).
  2. `calculate_circuit_params(formula_type, values)`: Computes Ohm's law, voltage dividers, LED current-limiting resistors, RC filter cutoff frequencies, and voltage regulator power dissipation.
  3. `generate_bom(components_list)`: Generates a Bill of Materials with estimated unit costs and total project budget.

* **Catalog / A2UI Displays**:
  * **Component Spec Cards**: Interactive cards with pinouts, operating voltage, and datasheet highlights.
  * **Pinout & Wiring Tables**: Step-by-step pin connection mapping (e.g., ESP32 GPIO21 -> OLED SDA).
  * **Bill of Materials (BOM) Table**: Itemized cost breakdown table with total cost.

* **Image Generation (Imagen 3)**:
  * Generates 3D PCB layout previews, schematic block diagrams, and custom 3D hardware enclosure concept renders.

* **Code Sandbox (Python Compute)**:
  * Runs Python code to model battery discharge curves, sum total system power consumption under sleep/active cycles, and model heat dissipation across linear regulators.

---

### Implementation Configuration

* **Core Rails (Everyone)**: Memory, Function Tools, Evaluation, Deployment, Frontend
* **Stretch Menu (Pick Later)**: Interactive A2UI Cards, Imagen 3 Visual Previews, Python Code Sandbox
* **First Eval Question**: *"Design an ESP32-based outdoor weather station with a BME280 sensor and a 128x64 OLED display, powered by a 3.7V LiPo battery. Calculate the estimated battery life in hours and output the full Bill of Materials with pricing."*
