import json
from pathlib import Path


TEMPLATE_METADATA = Path("template")

with open(TEMPLATE_METADATA, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# check mandatory fields
required_fields = ["command", "display_name"]
faulting_fields = []
for field in required_fields:
    if field not in metadata:
        faulting_fields.append(field)

if len(faulting_fields):
    raise AttributeError(f"Some required fields are not present in the metadata.json file: {faulting_fields}")


# check field formats
assert type(metadata["command"]) == str

assert "dependencies" in metadata or \
       type(metadata["dependencies"]) == list

assert "topic" in metadata or \
       type(metadata["topic"]) == list

assert "methodology" in metadata or \
       type(metadata["methodology"]) == list

assert "keywords" in metadata or \
       type(metadata["keywords"]) == list


# check possible values of command field
assert metadata["command"] in ["init", "generate"]
