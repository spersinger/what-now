from CalendarEvent import *
from typing import List

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
            group.append(event)
            event.date_range = event.get_next_occurrence_dates()
            if event.is_last_occurrence():
                break
        
        # append the group to the group list
        self.events.append(group)

            
    
    # performs the tasks set by the command
    # ex. create/modify/delete event
    def perform_command(self, command):
        pass
    
    
    # TESTING: 
    # add some manual data to the schedule
    def TEST_SET_SCHEDULE(self):
        
        name = "not senior project 2"
        desc = None
        notifs = [NotificationTime(5)]
        dates = DateRange(Date.today(), Date.today())
        times = TimeRange(Time(16), Time(16, 50))
        
        rep_type = RepeatCycle(TimeType.WEEKS, {Day.T, Day.W})
        rep_dur = RepeatDuration(DurationType.NUM_TIMES, 3)
        repeat = Repeat(rep_type, rep_dur)
        
        event = CalendarEvent(name, desc, notifs, dates, times, repeat)
        
        self.add_event(event)
        
    # TESTING: prints the schedule to the console
    def TEST_PRINT_SCHEDULE(self):
        for group in self.events:
            
            print("\n------ EVENT GROUP ------")
            for event in group:
                print(event)