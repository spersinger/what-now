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
        
        # repeating event: create all as individual events
        if event.repeat is not None:
            group = [] # will be appended to "events"
            
            # add copies of events based on duration, then repeat type
            if event.repeat.duration.dur_type == DurationType.NUM_TIMES:
                num_events = event.repeat.duration.value

                # add initial event to group
                group.append(event)
                
                # add copies of the event to the group
                for i in range (num_events):
                    # create next copy
                    next_event: CalendarEvent = event
                    
                    # correctly adjust date next based on repeat type
                    match(next_event.repeat.cycle.type):
                        case TimeType.DAYS: # every day: the next day
                            next_event.date_range.start_date.day += 1
                            next_event.date_range.end_date.day += 1
                        case TimeType.WEEKS: # days/week: next day in U M T W R F S cycle
                            pass
                        case TimeType.MONTHS:
                            pass
                        case TimeType.YEARS:
                            pass
                        case _:
                            print("error: cycle type not permitted (only days, weeks, months, years)")
                    
                    pass
                
            else: # == DurationType.UNTIL_DATE
                pass

            
    
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