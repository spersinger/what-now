from CalendarEvent import *
from typing import List
from Command import Command, Response, CommandType, StatusCode
from copy import deepcopy
from difflib import SequenceMatcher
import calendar

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
        
        # if no date, assume search is for whole group
        # TODO: necessary? figure out use case if so
        if search_term.date_range is None:
            for g_idx, group in enumerate(self.events):
                if group[0].name == search_term.name:
                    return (group[0], g_idx, None)
            
        # otherwise, find single event match
        for g_idx, group in enumerate(self.events):
            for e_idx, event in enumerate(group):
                
                name_close = SequenceMatcher(None, name, event.name).ratio() >= 0.8
                
                # if search tearm contains nothing except name, return group index (event 0)
                if search_term.date_range is None and name_close:
                    return (self.events[g_idx][0], g_idx, None)
                
                # if date matches, return that event
                if event.date_range.contains_date(search_term.date_range.start_date):
                    return (self.events[g_idx][e_idx], g_idx, e_idx)
        
        # no match found
        return None
    
    def get_for_date(self, date: Date) -> List[CalendarEvent]:
        result = []
        for group in self.events:
            for ev in group:
                if ev.date_range.contains_date(date):
                    result.append(ev)
        return result

    def get_event_counts(self, year, month) -> dict:
        counts = {}
        for group in self.events:
            for ev in group:
                for day in range(1, calendar.monthrange(year, month)[1] + 1):
                    d = Date(year, month, day)
                    if self._event_occurs_on(ev, d):
                        counts[day] = counts.get(day, 0) + 1
        return counts

    def _event_occurs_on(self, ev: CalendarEvent, d: Date) -> bool:
        return ev.date_range.contains_date(d)

    def get_days_with_events(self, year: int, month: int) -> Set[int]:
        days = set()
        for group in self.events:
            for ev in group:  # <-- iterate into the group
                for day in range(1, calendar.monthrange(year, month)[1] + 1):
                    d = Date(year, month, day)
                    if self._event_occurs_on(ev, d):
                        days.add(day)
        return days
    
    def add_event(self, event:CalendarEvent):
        
        # create group to hold event(s)
        group: List[CalendarEvent] = []
        num_repeats = -1
        
        # add any recurrences of the event to the group (do while)
        # (handle num_events duration case separately here)
        while True:
            group.append(deepcopy(event))
            num_repeats += 1
            if event.repeat == None:
                break
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
        if new_event.name is None: new_event.name = curr.name
        if new_event.description is None: new_event.description = curr.description
        if new_event.notif_times is None: new_event.notif_times = curr.notif_times
        
        # more complicated replacements (dates, times, repeat)
        
        # TODO: handle edge cases
        # (ex. keeping event length the same when changing only one time)
        
        if new_event.date_range is None:
            new_event.date_range = curr.date_range
        else:
            if new_event.date_range.start_date is None:
                new_event.date_range.start_date = curr.date_range.start_date
            if new_event.date_range.end_date is None:
                new_event.date_range.end_date = curr.date_range.end_date

        if new_event.time_range is None:
            new_event.time_range = curr.time_range
        else:
            if new_event.time_range.start_time is None:
                new_event.time_range.start_time = curr.time_range.start_time
            if new_event.time_range.end_time is None:
                new_event.time_range.end_time = curr.time_range.end_time

        if new_event.repeat is None:
            new_event.repeat = curr.repeat
        else:
            if new_event.repeat.cycle is None:
                new_event.repeat.cycle = curr.repeat.cycle
            if new_event.repeat.duration is None:
                new_event.repeat.duration = curr.repeat.duration
        
        # replace
        if index is None: # whole group
            self.delete_event(group)
            self.add_event(new_event)
        else: # single event
            self.events[group][index] = new_event

            
    
    # performs the tasks set by the command
    # ex. create/modify/delete event
    def perform_command(self, command:Command) -> Response:
        response = Response()
    
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
                assert type(command.data) == tuple and len(command.data) == 2
                
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
