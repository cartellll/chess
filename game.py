import json
import jsonschema
from jsonschema import validate


schema = {
    "type": "object",
    "properties": {
        "horses": {
            "type": "array",
            "minItems": 9,
            "maxItems": 16,
            "items": [
                {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "color": {"type": "number"}
                    },
                    "required": [
                        "x",
                        "y",
                        "color"
                    ],
                    "additionalProperties": False
                }
            ]
        },
        "move":{"type": "number"
        }
    },
    "required": [
        "horses",
        "move"
    ]
}
           

def parse_data(data):
    return data['horses'],data['move']

         
def validate_json(data):
   
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError:
        return False
    return True

def load_game_state_from_json(json_file_path):
  
    with open(json_file_path) as json_file:
        try:
            data = json.load(json_file)
            if validate_json(data):
                return True, data
        except json.decoder.JSONDecodeError:
            pass
    return False, None


def save_game_state_to_json(massHorses, move, gameEnd, json_file_path):
   
    data = {'horses': [],'move':1}
    data['horses']=massHorses
    data['move']=move
    with open(json_file_path, 'w') as outfile:
        if(not gameEnd):
            json.dump(data, outfile, indent=4)
        else:
            json.dump("", outfile, indent=4)

