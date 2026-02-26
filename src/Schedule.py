from CalendarEvent import *
from typing import List
from Command import Command, Response, CommandType
from copy import deepcopy
from difflib import SequenceMatcher

# contains all of a user's events
# purpose: manage calendar events
class Schedule():
    events: List[List[CalendarEvent]] # repeating events grouped together
    
    def __init__(self):
        self.events = []
        
    # returns a list of close matches for the given input (matches include indices)
    # search by name and optional date
    def search_events(self, name:str, date:Date|str=None) -> List[Tuple[CalendarEvent, int, int]]:
        if date is not None and type(date) == str:
            date = DateRange._str_to_date(date)
        
        matches: List[Tuple[CalendarEvent, int, int]] = list();
        
        for g_idx, group in enumerate(self.events):
            for e_idx, event in enumerate(group):
                
                # check items by precedence: name (calculate match), date
                name_close = SequenceMatcher(None, name, event.name).ratio() >= 0.8
                if date is not None:
                    contains_date = event.date_range.contains_date(date)
                else:
                    contains_date = True
                
                if name_close and contains_date:
                    matches.append((event, g_idx, e_idx))
        
        return matches
                    
                
    
    # returns the group and individual indices of a specific event
    # all parameters must match
    def get_event_indices(self, event:CalendarEvent) -> Tuple[int,int]:
        for g_idx, group in enumerate(self.events):
            for e_idx, ev in enumerate(group):
                if event == ev: return (g_idx, e_idx)
        return None
    
    def add_event(self, event:CalendarEvent):
        
        # create group to hold event(s)
        group: List[CalendarEvent] = []
        num_repeats = -1
        
        # add any recurrences of the event to the group (do while)
        # (handle num_events duration case separately here)
        while True:
            group.append(deepcopy(event))
            num_repeats += 1
            event.date_range = event.get_next_occurrence_dates()
            if event.date_range == None:
                break
            if (event.repeat.duration.dur_type == DurationType.FOREVER or
                event.repeat.duration.dur_type == DurationType.NUM_TIMES) \
                and num_repeats == event.repeat.duration.value:
                break
        
        # append the group to the group list
        self.events.append(group)
    
    # leave index None to delete whole group
    def delete_event(self, group:int, index:int=None):
        if index is None:
            # delete entire group
            del self.events[group]
        else:
            # delete single event
            del self.events[group][index]

    # leave index None to modify whole group
    # (just deletes and creates a new series if group only)
    def modify_event(self, new_event: CalendarEvent, group:int, index:int=None):
        if index is None:
            # replace whole group
            self.delete_event(group)
            self.add_event(new_event)
        else:
            # replace single event
            self.events[group][index] = new_event

            
    
    # performs the tasks set by the command
    # ex. create/modify/delete event
    def perform_command(self, command:Command) -> Response:
        response = Response(command.id)
    
        # yeah whatever we have to do this instead of 
        # just using the enums like it should be
        match command.c_type.name:
            case "SEARCH":
                pass
            case "EDIT":
                pass
            case "ADD":
                self.add_event(command.event)
                response.status_details = "event was added to calendar."
            case "DELETE":
                pass
            case _:
                print("not supposed to happen")
        
        return response
        
    
    
    # TESTING: 
    # add some manual data to the schedule
    def TEST_SET_SCHEDULE(self):
        
        
        # should be: 17 19 24 26 3 5
        event = CalendarEvent(
            "not senior project 2",
            "aoeusnth aoeusnth aoeusnth aoeusnth",
            [NotifTime(5)],
            DateRange("2/17", "2/18"),
            TimeRange("2:00p", "2:50p"),
            Repeat("week tr", "until 3/5")
        )
        
        self.add_event(event)
        
    # TESTING: prints the schedule to the console
    def __str__(self):
        result: str = ""
        for group in self.events:
            
            result += "\n\n\n------ EVENT GROUP ------\n"
            result += "total: " + str(len(group)) + " event(s)\n\n"
            for event in group:
                result += str(event) + "\n"
            
        return result