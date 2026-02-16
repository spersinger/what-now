from CalendarEvent import CalendarEvent
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
    """Holds information about an event and what to do with it."""
    
    id: int # unique to each command
    sent: bool # whether it has been sent to schedule or not
    type: CommandType
    event: CalendarEvent
    
    
# a status code from the schedule
class StatusCode(Enum):
    SUCCESS = 0
    ERROR = 0
    
# response
# holds information returned by schedule
# correlates to exactly one command
class Response:
    """Holds information about the status of a Command."""
    command_id: int
    status: StatusCode
    status_details: str
    data: Tuple[int]
    
    
# command interpreter
# transforms text input into a list of commands (to eventually send to the schedule)
class CommandInterpreter:
    
    # commands to be sent to the schedule
    commands: List[Command]
    
    def __init__(self):
        self.commands = List()
    
    # interpret text input and create one or more commands based on it
    # uses AI model, slow (but can interpret for voice input)
    def interpret_text(self, text:str):
        pass

    # manually add command to queue
    # much faster (no AI model use)
    def add_command(self, command:Command):
        self.commands.append(command)
    
    def handle_response(self, response:Response):
        pass
    
    def get_next_unsent_command(self) -> Command:
        index = 0
        while index < len(self.commands):
            candidate = self.commands[index]
            if not candidate.sent:
                candidate.sent = True
                return candidate
            index += 1
        return None
        