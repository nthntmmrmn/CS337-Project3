import json

with open('lists.json') as f:
  data = json.load(f)

PRIMARY_METHODS = data['PRIMARY_METHODS']
OTHER_METHODS = data['OTHER_METHODS']
TOOLS = data['TOOLS']
