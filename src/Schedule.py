from CalendarEvent import *
from typing import List
from Command import Command, Response, CommandType
from copy import deepcopy

# contains all of a user's events
# purpose: manage calendar events
class Schedule():
    events: List[List[CalendarEvent]] # repeating events grouped together
    
    def __init__(self):
        self.events = []
        
    # returns a list of best matches for the given input
    # search by name, date, 
    def search_events(self, name:str=None, ) -> List[CalendarEvent]:
        pass
    
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
            if event.is_last_occurrence():
                break
            if event.repeat.duration.dur_type == DurationType.NUM_TIMES and num_repeats == event.repeat.duration.value:
                break
        
        # append the group to the group list
        self.events.append(group)

            
    
    # performs the tasks set by the command
    # ex. create/modify/delete event
    def perform_command(self, command:Command) -> Response:
        response: Response = Response(command.id)
        
        if command.type == CommandType.ADD:
            raise ValueError("seriously wtf is this")
        
        match command.type:
            case CommandType.SEARCH:
                pass
            case CommandType.EDIT:
                pass
            case CommandType.ADD: # ???????????????????????????????????????
                # for SOME reason
                # during testing, when command.type is set to CommandType.ADD
                # IT DOESNT MATCH HERE
                # glad the rest seems to work ig but like wtf
                # ive verified it in so many ways, i have a breakpoint here
                # and it says exactly that the command type is what i think it is
                self.add_event(command.event)
                response.status_details = "event was added to calendar."
            case CommandType.DELETE:
                pass
            case _:
                self.add_event(command.event)
                response.status_details = "event was added to calendar."
        
        return response
        
    
    
    # TESTING: 
    # add some manual data to the schedule
    def TEST_SET_SCHEDULE(self):
        
        event = CalendarEvent(
            "not senior project 2",
            "aoeusnth aoeusnth aoeusnth aoeusnth",
            [NotifTime(5)],
            DateRange(Date(2026, 2, 16), Date(2026, 2, 16)),
            TimeRange(Time(14), Time(15)),
            Repeat(
                RepeatCycle(TimeType.WEEK, {Day.M, Day.R}),
                RepeatDuration(DurationType.NUM_TIMES, (3, Date(2026,2,16)))
            )
        )
        
        self.add_event(event)
        
        event.name = "irresponsible computing"
        event.description = "they teach you to be evil"
        event.notification_times = [NotifTime(30, TimeType.HOUR), NotifTime(1)]
        event.date_range = DateRange(Date(2026, 2, 28), Date(2026, 3, 1))
        event.repeat.duration = RepeatDuration(DurationType.UNTIL_DATE, Date(2026, 5, 17))
        
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