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
# TODO: figure out how modifying events works
class Command:
    """Holds information about an event and what to do with it."""
    
    id: int # unique to each command
    sent: bool # whether it has been sent to schedule or not
    c_type: CommandType
    event: CalendarEvent
    event_indices: Tuple[int, int]
    
    def __init__(self, id:int, c_type:CommandType, event:CalendarEvent, indices:Tuple[int, int]=None):
        self.id = id
        self.sent = False
        self.c_type = c_type
        self.event = event
        self.event_indices = indices
    
    
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
    data = None
    
    def __init__(self, id:int):
        self.command_id = id
        self.status = StatusCode.SUCCESS
        self.status_details = ""
        self.data = None
    
    
    
# command interpreter
# transforms text input into a list of commands (to eventually send to the schedule)
class CommandInterpreter:
    
    # commands to be sent to the schedule
    commands: List[Command]
    
    def __init__(self):
        self.commands = list()
    
    # interpret text input and create one or more commands based on it
    # uses AI model, slow (but can interpret for voice input)
    def interpret_text(self, text:str):
        pass

    # manually add command to queue
    # much faster (no AI model use)
    def add_command(self, command:Command):
        self.commands.append(command)
    
    
    # TODO: handle all cases
    # for now, only handle the showcase test case (success from adding event)
    def handle_response(self, response:Response):
        
        # get corresponding command
        command: Command = None
        for c in self.commands:
            if c.id == response.command_id:
                command = c
        
        if command is None:
            # error: command was removed before schedule finished processing (shouldn't happen)
            print("schedule response has no corresponding command")
            return

        # search, edit, add, delete
        match command.c_type:
            case CommandType.SEARCH:
                pass
            case CommandType.EDIT:
                pass
            case CommandType.ADD:
                if response.status == StatusCode.SUCCESS:
                    # success: remove command from list
                    self.commands.remove(command)
                else:
                    pass
            case CommandType.DELETE:
                pass
            case _:
                print("error: unexpected command type")
                return
        
    
    def get_next_unsent_command(self) -> Command:
        index = 0
        while index < len(self.commands):
            candidate = self.commands[index]
            if not candidate.sent:
                candidate.sent = True
                return candidate
            index += 1
        return None
        