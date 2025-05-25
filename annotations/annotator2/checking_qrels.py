import numpy as np
import json

relevances = {}

with open('qrels.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line.strip())
        if relevances.get(data["id"]) is None:
            relevances[data["id"]] = {}
        relevances[data["id"]].update({
            data['document']: {k: v for k, v in data["relevances"].items() if v != -1}
        })

print(relevances)

