from CalendarEvent import CalendarEvent, Date
from enum import Enum
from typing import Tuple, List

class CommandType(Enum):
    """Represents the different functions a Command can process."""
    
    SEARCH = 0
    EDIT = 1
    ADD = 2
    DELETE = 3



# command
# holds information about one request to send to the schedule.
class Command:
    """
    Holds information about an event and what to do with it.
    
    Command Types:
    --------------
    
    SEARCH: 
        - retrieve information about an event.
        - data is a CalendarEvent whose entries are used as search terms
        
    EDIT:
        - modify an existing event or series of events.
        - data is a pair of CalendarEvents (tuple):
            - first's fields are used as search terms (find event to modify)
            - second is what fields to modify (to leave unchanged, use None)
    
    ADD: 
        - add a new event to the schedule. 
        - data is the CalendarEvent to add (if repeating, will add all repeats).

    
    DELETE: 
        - remove an event or series of events.
        - data is a CalendarEvent whose search terms are used to find the event.
    
    """
    
    c_type: CommandType
    data: CalendarEvent | Tuple[CalendarEvent, CalendarEvent] # if 2: first is search, 2nd is modifier
    
    def __init__(self, c_type:CommandType, data:CalendarEvent|Tuple[CalendarEvent, CalendarEvent]):
        self.c_type = c_type
        self.data = data
    
    
    
# a status code from the schedule
class StatusCode(Enum):
    SUCCESS = 0
    ERROR = 0
    
    
    
# response
# holds information returned by schedule
# correlates to exactly one command
class Response:
    """Holds information about the status of a Command."""
    status: StatusCode
    status_details: str
    data = None
    
    def __init__(self):
        self.status = StatusCode.SUCCESS
        self.status_details = ""
        self.data = None
    
    
    
# command interpreter
# transforms text input into a list of commands (to eventually send to the schedule)
class CommandInterpreter:
    """Transforms text input into a series of Commands."""
    
    # commands to be sent to the schedule
    commands: List[Command]
    
    def __init__(self):
        self.commands = list()
    
    # interpret text input and create one or more commands based on it
    # (use AI model to transform text into list of commands)
    def generate_commands(self, text:str):
        pass

    # manually add command to queue
    # much faster (no AI model use)
    def add_command(self, command:Command):
        self.commands.append(command)