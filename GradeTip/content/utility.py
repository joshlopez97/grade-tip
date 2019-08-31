import json
from datetime import datetime


def get_time():
    return json.dumps(datetime.now(), default=lambda obj: (
        obj.isoformat()
        if isinstance(obj, (datetime, datetime.date))
        else None
    )).strip("\"")
