from build_universal_labels import build_custom_sheet
import json

with open("my_labels.json", "r", encoding="utf-8") as f:
    labels = json.load(f)

build_custom_sheet(labels)

