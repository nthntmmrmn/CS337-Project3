import json

with open('lists.json') as f:
  data = json.load(f)
with open('veg_transforms.json') as f:
  data2 = json.load(f)
with open('lactose_free_transforms.json') as f:
  data3 = json.load(f)

PRIMARY_METHODS = data['PRIMARY_METHODS']
OTHER_METHODS = data['OTHER_METHODS']
TOOLS = data['TOOLS']
VEG_SUBS = data2
LACTOSE_FREE_SUBS = data3
# MEAT = data['MEAT']
# FISH = data['FISH']
