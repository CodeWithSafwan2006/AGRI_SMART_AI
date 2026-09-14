"""Ordered class list — must match folder names under data/train after curation."""

CLASS_NAMES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___healthy",
    "Bell_pepper___Bacterial_spot",
    "Bell_pepper___healthy",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Gray_leaf_spot",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___healthy",
]

# PlantVillage raw/color directory names (when different from CLASS_NAMES)
SOURCE_DIR_BY_CLASS = {
    "Bell_pepper___Bacterial_spot": "Pepper,_bell___Bacterial_spot",
    "Bell_pepper___healthy": "Pepper,_bell___healthy",
    "Corn_(maize)___Gray_leaf_spot": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
}
