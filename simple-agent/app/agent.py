# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from google.cloud import firestore
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.6-flash"

_db = None

def get_firestore_client():
    global _db
    if _db is None:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-61ad25d47240")
        _db = firestore.Client(project=project_id)
    return _db


def get_material_spec(material_id: str) -> dict:
    """Fetch material technical properties from the Firestore materials collection.

    Args:
        material_id: Material identifier such as 'pla', 'petg', or 'tpu'.

    Returns:
        A dictionary containing material specs (density, tensile strength, print temps, UV resistance, cost).
    """
    db = get_firestore_client()
    doc = db.collection("materials").document(material_id.lower()).get()
    if doc.exists:
        return doc.to_dict()
    return {"error": f"Material '{material_id}' not found in database. Available: pla, petg, tpu."}


def get_printer_spec(printer_id: str) -> dict:
    """Fetch 3D printer hardware specs from the Firestore printers collection.

    Args:
        printer_id: Printer identifier such as 'bambu_x1c', 'ender_3_v2', or 'prusa_mk4'.

    Returns:
        A dictionary containing printer specs (build volume, default nozzle size, max speed, enclosure).
    """
    db = get_firestore_client()
    doc = db.collection("printers").document(printer_id.lower()).get()
    if doc.exists:
        return doc.to_dict()
    return {"error": f"Printer '{printer_id}' not found in database. Available: bambu_x1c, ender_3_v2, prusa_mk4."}


def list_slicer_presets() -> list[dict]:
    """Retrieve all available slicer profile presets from the Firestore slicer_presets collection.

    Returns:
        A list of dictionaries with preset details (layer height, wall loops, infill %, pattern, use cases).
    """
    db = get_firestore_client()
    docs = db.collection("slicer_presets").stream()
    return [doc.to_dict() for doc in docs]


def consult_3d_printing_guide(query: str) -> str:
    """Grounding tool: Search the official 3D Printing Troubleshooting & Slicing Reference Guide.

    Args:
        query: What to look up (e.g., 'stringing', 'petg temperature', 'warping', 'gyroid infill').

    Returns:
        Relevant passages retrieved from the 3D printing reference guide.
    """
    guide_path = os.path.join(os.path.dirname(__file__), "..", "scratch", "3d_printing_handbook.txt")
    if not os.path.exists(guide_path):
        return "Reference guide file not found."
    with open(guide_path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split("\n\n")
    query_terms = [q.lower() for q in query.split() if len(q) > 2]
    matched = []
    for sec in sections:
        sec_lower = sec.lower()
        if any(term in sec_lower for term in query_terms):
            matched.append(sec.strip())

    if matched:
        return "\n\n---\n\n".join(matched[:3])
    return content[:1200]


def analyze_printability_and_cost(volume_cm3: float, material_id: str, wall_loops: int = 3, infill_percent: float = 20.0) -> dict:
    """Run physics and slicing calculations to compute filament weight, print time, and cost.

    Args:
        volume_cm3: Total solid volume of the 3D model in cubic centimeters (cm³).
        material_id: Material identifier ('pla', 'petg', or 'tpu').
        wall_loops: Number of outer perimeter wall loops (default 3).
        infill_percent: Infill density percentage (0 to 100, default 20.0).

    Returns:
        A dictionary with calculated weight (grams), print time estimate, material cost ($), and structural rating.
    """
    material_info = get_material_spec(material_id)
    if "error" in material_info:
        density = 1.25
        cost_per_kg = 22.0
    else:
        density = material_info.get("density_g_cm3", 1.25)
        cost_per_kg = material_info.get("cost_per_kg", 22.0)

    effective_density_factor = 0.2 + (infill_percent / 100.0) * 0.8
    total_weight_g = round(volume_cm3 * density * effective_density_factor, 2)
    estimated_cost_usd = round((total_weight_g / 1000.0) * cost_per_kg, 2)
    estimated_time_minutes = round(total_weight_g * 2.5 + (wall_loops * 5), 1)

    return {
        "volume_cm3": volume_cm3,
        "material": material_id.upper(),
        "calculated_weight_g": total_weight_g,
        "estimated_cost_usd": estimated_cost_usd,
        "estimated_print_time_hours": round(estimated_time_minutes / 60.0, 2),
        "wall_loops": wall_loops,
        "infill_percent": infill_percent,
        "structural_rating": "High Strength" if (wall_loops >= 4 and infill_percent >= 25) else "Standard Duty"
    }


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are PrintCraft 3D, an expert AI 3D-printing and slicer assistant.
Your goal is to help users analyze 3D prints, select optimal materials, look up 3D printer specifications, troubleshoot print failures, and calculate slicer estimates.
Always call `consult_3d_printing_guide` to ground your advice on troubleshooting or temperature/slicing questions.
Call `analyze_printability_and_cost` when calculating print times, filament weights, or cost estimates.
Use `get_material_spec`, `get_printer_spec`, and `list_slicer_presets` to query structured database records.""",
    tools=[get_material_spec, get_printer_spec, list_slicer_presets, consult_3d_printing_guide, analyze_printability_and_cost],
)

app = App(
    root_agent=root_agent,
    name="app",
)


