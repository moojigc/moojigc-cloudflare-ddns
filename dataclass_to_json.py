import dataclasses
import json


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def dataclass_to_json(dataclass_instance):
    return json.dumps(dataclass_instance, cls=EnhancedJSONEncoder)
