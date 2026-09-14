"""Basic precautionary guidance per disease class (display name → advice)."""

from model.labels import CLASS_NAMES

DISPLAY = {name: name.replace("___", " — ").replace("_", " ") for name in CLASS_NAMES}

PRECAUTIONS = {
    "Tomato___Early_blight": "Remove infected lower leaves; improve airflow; avoid wetting foliage; rotate crops next season.",
    "Tomato___Late_blight": "Remove and destroy affected plants; do not compost; reduce humidity and overhead irrigation.",
    "Tomato___Leaf_Mold": "Increase ventilation in greenhouses; avoid dense planting; water at soil level.",
    "Tomato___Bacterial_spot": "Use disease-free seed; sanitize tools; avoid working plants when wet.",
    "Tomato___healthy": "No disease signs detected — continue regular scouting and balanced fertilization.",
    "Potato___Early_blight": "Remove infected foliage; ensure crop rotation; apply preventive fungicide if recommended locally.",
    "Potato___Late_blight": "Destroy infected tubers and vines; monitor weather for blight-favorable conditions.",
    "Potato___healthy": "Plants look healthy — maintain good drainage and avoid over-irrigation.",
    "Corn_(maize)___Common_rust_": "Plant resistant hybrids if available; remove heavily infected leaves where practical.",
    "Corn_(maize)___Gray_leaf_spot": "Rotate with non-host crops; manage residue; scout lower leaves regularly.",
    "Corn_(maize)___healthy": "No rust/leaf spot signs — monitor during humid periods.",
    "Apple___Apple_scab": "Prune for airflow; remove fallen leaves; consider scab-tolerant cultivars.",
    "Apple___Black_rot": "Remove mummified fruit and cankers; sanitize pruning tools.",
    "Apple___healthy": "No scab/rot signs — maintain orchard sanitation.",
    "Grape___Black_rot": "Remove infected berries and mummies; improve canopy airflow.",
    "Grape___healthy": "Vines appear healthy — continue canopy management.",
    "Bell_pepper___Bacterial_spot": "Use pathogen-free transplants; avoid overhead irrigation; rotate fields.",
    "Bell_pepper___healthy": "No bacterial spot signs — keep foliage dry when possible.",
}


def precaution_for(class_label: str) -> str:
    return PRECAUTIONS.get(class_label, "Consult local extension services for crop-specific treatment guidance.")


def display_name(class_label: str) -> str:
    return DISPLAY.get(class_label, class_label)
