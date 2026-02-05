from enum import Enum
from datetime import date as Date, time as Time
from typing import List

# enum type for referring to different notification
# timespan lengths
class TimeType(Enum):
    MINUTES = 0
    HOURS = 1
    DAYS = 2
    WEEKS = 3

# holds a number of minutes/hours/days/weeks
# before an event to send the user a notification for
class NotificationTime():
    timespan_type: TimeType
    num_timespans: int
    
    def __init__(self, num:int, type:TimeType=TimeType.MINUTES):
        if(num < 0): raise ValueError("Number of timespans must be non-negative.")
        self.num_timespans = num
        self.timespan_type = type
        
    def __setattr__(self, name, value):
        if name == "num_timespans" and value < 0:
            raise ValueError("Number of timespans must be non-negative.")
        super().__setattr__(name, value)



# parent class for the 3 different kinds of events
class CalendarEvent():
    name: str
    description: str | None
    notification_times: List[NotificationTime] | None
    
    def __init__(
                self, 
                name:str, 
                desc:str|None=None, 
                notifs:List[NotificationTime]|None=None
            ):
        self.name = name
        self.description = desc
        self.notification_times = notifs



# for events fully contained within one calendar day
#
# TODO: enforce data rules
#   - end_time must be after start_time (cannot be same; that would be a reminder)
#     (ux note: if user does try to input an event with same start/end time, 
#      transform it into a reminder instead of using an error)
class SingleDayEvent(CalendarEvent):
    date: Date
    start_time: Time
    end_time: Time
    
    def __init__(
                self, name:str, 
                date:Date, 
                start_time:Time, end_time:Time, 
                desc:str|None=None, 
                notifs:List[NotificationTime]|None=None
            ):
        super().__init__(name, desc, notifs)
        self.date = date
        self.start_time = start_time
        self.end_time = end_time



# for events spanning more than 1 day
# (displayed as a banner in the UI)
#
# TODO: enforce data rules
#   - end_date cannot be before start_date
#   - end_time cannot be before start_time
class MultiDayEvent(CalendarEvent):
    start_date: Date
    end_date: Date
    start_time: Time | None
    end_time: Time | None
    
    def __init__(
                self, name:str, 
                start_date:Date, end_date:Date, 
                start_time:Time|None=None, end_time:Time|None=None,
                desc:str|None=None,
                notifs:List[NotificationTime]|None=None
            ):
        super().__init__(name, desc, notifs)
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time



# reminders represented by instants (not timespans)
class ReminderEvent(CalendarEvent):
    date: Date
    time: Time
    
    def __init__(
                self, name:str, 
                date:Date, time:Time,
                desc:str|None=None,
                notifs:List[NotificationTime]|None=None
            ):
        super().__init__(name, desc, notifs)
        self.date = date
        self.time = time