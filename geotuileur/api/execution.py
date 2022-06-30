from dataclasses import dataclass
from datetime import datetime


@dataclass
class Execution:
    id: str
    status: str
    name: str
    start: datetime = None
    finish: datetime = None
