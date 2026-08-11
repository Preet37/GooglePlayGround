import os
from google.cloud import firestore

def seed_database():
    db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-61ad25d47240"))
    
    # 1. Seed Materials Collection
    materials_ref = db.collection("materials")
    materials_data = [
        {
            "id": "pla",
            "name": "PLA (Polylactic Acid)",
            "density_g_cm3": 1.24,
            "tensile_strength_mpa": 50,
            "nozzle_temp_c": 210,
            "bed_temp_c": 60,
            "uv_resistant": False,
            "cost_per_kg": 20.0,
            "best_for": "General prototyping, fast draft prints, indoor models"
        },
        {
            "id": "petg",
            "name": "PETG (Polyethylene Terephthalate Glycol)",
            "density_g_cm3": 1.27,
            "tensile_strength_mpa": 53,
            "nozzle_temp_c": 240,
            "bed_temp_c": 80,
            "uv_resistant": True,
            "cost_per_kg": 25.0,
            "best_for": "Outdoor parts, mechanical brackets, water/chemical resistant parts"
        },
        {
            "id": "tpu",
            "name": "TPU (Thermoplastic Polyurethane)",
            "density_g_cm3": 1.21,
            "tensile_strength_mpa": 35,
            "nozzle_temp_c": 230,
            "bed_temp_c": 50,
            "uv_resistant": True,
            "cost_per_kg": 32.0,
            "best_for": "Flexible gaskets, phone cases, vibration dampeners"
        }
    ]
    for mat in materials_data:
        materials_ref.document(mat["id"]).set(mat)
    print("✅ Seeded materials collection")

    # 2. Seed Printers Collection
    printers_ref = db.collection("printers")
    printers_data = [
        {
            "id": "bambu_x1c",
            "name": "Bambu Lab X1-Carbon",
            "build_volume_mm": {"x": 256, "y": 256, "z": 256},
            "default_nozzle_mm": 0.4,
            "max_print_speed_mms": 500,
            "enclosure": True
        },
        {
            "id": "ender_3_v2",
            "name": "Creality Ender 3 V2",
            "build_volume_mm": {"x": 220, "y": 220, "z": 250},
            "default_nozzle_mm": 0.4,
            "max_print_speed_mms": 100,
            "enclosure": False
        },
        {
            "id": "prusa_mk4",
            "name": "Prusa MK4",
            "build_volume_mm": {"x": 250, "y": 210, "z": 220},
            "default_nozzle_mm": 0.4,
            "max_print_speed_mms": 200,
            "enclosure": False
        }
    ]
    for p in printers_data:
        printers_ref.document(p["id"]).set(p)
    print("✅ Seeded printers collection")

    # 3. Seed Slicer Presets Collection
    presets_ref = db.collection("slicer_presets")
    presets_data = [
        {
            "id": "structural_high_strength",
            "name": "High Strength Structural",
            "layer_height_mm": 0.20,
            "wall_loops": 4,
            "infill_percentage": 30,
            "infill_pattern": "gyroid",
            "top_bottom_layers": 5,
            "use_case": "Load-bearing brackets, gears, mechanical joints"
        },
        {
            "id": "standard_balanced",
            "name": "Standard Quality Balanced",
            "layer_height_mm": 0.20,
            "wall_loops": 2,
            "infill_percentage": 15,
            "infill_pattern": "grid",
            "top_bottom_layers": 4,
            "use_case": "General models, decorative parts, light-duty mounts"
        }
    ]
    for preset in presets_data:
        presets_ref.document(preset["id"]).set(preset)
    print("✅ Seeded slicer_presets collection")

if __name__ == "__main__":
    seed_database()
