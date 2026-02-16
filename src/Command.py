from CalendarEvent import CalendarEvent
from enum import Enum

class CommandType(Enum):
    SEARCH = 0
    EDIT = 1
    ADD = 2
    DELETE = 3

# command
# holds information about one request to send to the schedule.
class Command:
    type: CommandType
    event: CalendarEvent