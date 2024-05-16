import json


measures = {}

with open('ingredients.json', 'r') as file_json:
    data = json.load(file_json)

for ingredient in data:
    measurement_unit = ingredient['measurement_unit']
    measures[measurement_unit] = measures.get(measurement_unit, 0) + 1

with open('measures.json', 'w', encoding='utf-8') as file_json:
    data = json.dump(
        obj=measures,
        fp=file_json,
        indent=3,
        ensure_ascii=False
    )
