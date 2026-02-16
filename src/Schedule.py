from CalendarEvent import *
from typing import List
from Command import Response

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
        
        # add any recurrences of the event to the group (do while)
        while True:
            group.append(deepcopy(event))
            event.date_range = event.get_next_occurrence_dates()
            if event.is_last_occurrence():
                break
        
        # append the group to the group list
        self.events.append(group)

            
    
    # performs the tasks set by the command
    # ex. create/modify/delete event
    def perform_command(self, command) -> Response:
        pass
    
    
    # TESTING: 
    # add some manual data to the schedule
    def TEST_SET_SCHEDULE(self):
        
        event = CalendarEvent(
            "not senior project 2",
            "ounstah,.ul crtoaensuh aorseuh naotu ",
            [NotificationTime(5)],
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
        event.notification_times = [NotificationTime(30, TimeType.HOUR), NotificationTime(1)]
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