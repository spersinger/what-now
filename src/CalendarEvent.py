from enum import Enum
from datetime import date as Date, time as Time
from typing import List, Dict

# enum type for referring to different notification
# timespan lengths
class TimeType(Enum):
    MINUTES = 0
    HOURS = 1
    DAYS = 2
    WEEKS = 3

class TimeRange:
    start_time: Time
    end_time: Time

# class that holds a range of dates
class DateRange:
    start_date: Date
    end_date: Date
    
# class to hold semester start/end dates
class Semesters:
    terms: Dict # {str, DateRange}
    
# class to hold weekly repeat data
# repeat: days/week, days/month
class Repeat:
    pass
    

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


# represents a calendar event, possibly repeating
# TODO: how to handle changing 1 instance of a repeating event?
#       - solution 1: group similar instances together in schedule
#       - solution 2: 
class CalendarEvent():
    name: str
    description: str | None
    notification_times: List[NotificationTime] | None
    date_range: DateRange
    time_range: TimeRange
    repeat: Repeat | None
    
    
    def __init__(
                self, 
                name:str, 
                desc:str|None, 
                notifs:List[NotificationTime]|None,
                dates: DateRange,
                times: TimeRange,
                repeat: Repeat | None
            ):
        self.name = name
        self.description = desc
        self.notification_times = notifs
        self.date_range = dates
        self.time_range = times
        self.repeat = repeat