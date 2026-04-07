import yaml,json;
from jsonschema import validate
from pathlib import Path

schema = json.load(open("schemas/prompt.schema.json"))

for p in Path("prompts").glob("*.yaml"):
    data = yaml.safe_load(open(p))
    validate(instance=data, schema=schema)

print("All prompts valid")
