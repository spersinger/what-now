from CalendarEvent import *
from typing import List
from Command import Command, Response, CommandType, StatusCode
from copy import deepcopy
from difflib import SequenceMatcher

# contains all of a user's events
# purpose: manage calendar events
class Schedule():
    events: List[List[CalendarEvent]] # repeating events grouped together
    
    def __init__(self):
        self.events = []
        
        
        
    # returns the closest match;
    # search by name and optional date
    def search_events(self, search_term:CalendarEvent) -> Tuple[CalendarEvent, int, int]:
        name = search_term.name
        date = search_term.date_range.start_date # start date: search term
        
        match: Tuple[CalendarEvent, int, int]
        current_best: Tuple[float, bool] # closeness of name, whether date included
        
        # if no date, assume search is for whole group
        if search_term.date_range is None:
            for g_idx, group in enumerate(self.events):
                if group[0].name == search_term.name:
                    return (group[0], g_idx, None)
            
        # otherwise, find best single event match
        for g_idx, group in enumerate(self.events):
            for e_idx, event in enumerate(group):
                
                # if search tearm contains nothing except name, return group index (event 0)
                if search_term.date_range is None and search_term.name == event.name:
                    return (self.events[g_idx][0], g_idx, None)
                
                # check items by precedence: name (calculate match), date
                name_dist = SequenceMatcher(None, name, event.name).ratio() >= 0.8
                if date is not None:
                    contains_date = event.date_range.contains_date(date)
                else:
                    contains_date = True
                
                if name_dist > current_best[0] and not current_best[1]:
                    current_best = (name_dist, contains_date)
                    match = (event, g_idx, e_idx)
        
        return match
    
    
    
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
    def modify_event(self, mod:CalendarEvent, group:int, index:int=None):
        
        # get copy of first event recurrence
        curr = deepcopy(self.events[group][0 if index is None else index]) # make sure we get an object, not a reference

        new_event = mod
        
        # replacements
        if new_event.name == None: new_event.name = curr.name
        if new_event.description == None: new_event.description = curr.description
        if new_event.notification_times == None: new_event.notification_times = curr.notification_times
        
        # more complicated replacements (dates, times, repeat)
        
        
        # replace
        if index is None: # whole group
            self.delete_event(group)
            self.add_event(new_event)
        else: # single event
            self.events[group][index] = new_event

            
    
    # performs the tasks set by the command
    # ex. create/modify/delete event
    def perform_command(self, command:Command) -> Response:
        response = Response(command.id)
    
        # yeah whatever we have to do this instead of 
        # just using the enums like it should be
        match command.c_type.name:
            case "SEARCH":
                # ensure correct command data
                assert type(command.data) == CalendarEvent
                
                # search based on command's calendarevent
                response.data = self.search_events(command.event)
                if response.data is not None:
                    response.status = StatusCode.SUCCESS
                    response.status_details = "found matching event."
                else:
                    response.status = StatusCode.ERROR
                    response.status_details = "could not find matching event."

            case "EDIT":
                # ensure correct command data
                assert type(command.data) == Tuple[CalendarEvent, CalendarEvent]
                
                # first: search based on first event (search terms)
                response.data = self.search_events(command.data[0])
                if response.data is None:
                    response.status = StatusCode.ERROR
                    response.status_details = "could not find matching event to modify."
                else:
                    response.status = StatusCode.SUCCESS
                    response.status_details = "found matching event to modify."
                    
                    # second: modify event based on second event (modify by)
                    self.modify_event(command.data[1], *response.data[1:])

            case "ADD":
                # TODO: error handling?
                self.add_event(command.event)
                response.status = StatusCode.SUCCESS
                response.status_details = "event was added to calendar."

            # use incides to delete
            case "DELETE":
                
                # ensure correct command data
                assert type(command.data) == CalendarEvent
                
                # part 1: find event (or group) to delete
                response.data = self.search_events(command.data)
                if response.data is None:
                    response.status = StatusCode.ERROR
                    response.status_details = "could not find matching event(s) to delete."
                else:
                    response.status = StatusCode.SUCCESS
                    response.status_details = "found event(s) to delete."
                    self.delete_event(*(response.data[1:]))

            case _:
                print("not supposed to happen")
        
        return response
        
        
        
    def __str__(self):
        result: str = ""
        for group in self.events:
            
            result += "\n\n\n------ EVENT GROUP ------\n"
            result += "total: " + str(len(group)) + " event(s)\n\n"
            for event in group:
                result += str(event) + "\n"
            
        return result
    
# TODO: try/except with error propogation instead of None/assert usage? (everywehre, not just this file)