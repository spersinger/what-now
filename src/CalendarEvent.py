from enum import Enum
from datetime import date as Date, time as Time
from typing import List, Dict, Set

# enum type for referring to different notification
# timespan lengths
class TimeType(Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    
class Day(Enum):
    SUNDAY    = SUN = U = 0
    MONDAY    = MON = M = 1
    TUESDAY   = TUE = T = 2
    WEDNESDAY = WED = W = 3
    THURSDAY  = THU = R = 4
    FRIDAY    = FRI = F = 5
    SATURDAY  = SAT = S = 6

class TimeRange:
    start_time: Time
    end_time: Time
    
    def __init__(self, t1:Time, t2:Time):
        self.start_time = t1
        self.end_time = t2
        
    def __str__(self):
        return str(self.start_time) + " -> " + str(self.end_time)

# class that holds a range of dates
class DateRange:
    start_date: Date
    end_date: Date
    
    def __init__(self, d1:Date, d2:Date):
        self.start_date = d1
        self.end_date = d2

    
    def __str__(self):
        return str(self.start_date) + " -> " + str(self.end_date)
    
# class to hold semester start/end dates
class Semesters:
    terms: Dict # {str, DateRange}

class RepeatCycle():
    type: TimeType
    set: Set[Date] | Set[Day]
    
    def __init__(self, type:TimeType, set: Set[Date] | Set[Day]):
        self.type = type
        self.set = set
    
    def __str__(self):
        if self.type == TimeType.DAYS:
            return "every day"
        elif self.type == TimeType.WEEKS:
            return "every " + (str(day) + ", " for day in self.set)
        elif self.type == TimeType.MONTHS:
            return "every month on days " + (str(date.day) + ", " for date in self.set)
        else: # self.type == TimeType.YEARS
            return "every year on " + (str(date) + ", " for date in self.set)
    
    
class DurationType(Enum):
    NUM_TIMES = "times"
    UNTIL_DATE = "until"
    
class RepeatDuration:
    dur_type: DurationType
    value: int | Date | None
    
    def __init__(self, type:DurationType, value: int | Date | None):
        self.dur_type = type
        self.value = value
        
    def __str__(self):
        if self.value is None:
            return "once"
        elif type(self.value) is int:
            return self.value + " times"
        else: # type(self.value) is Date
            return "until " + self.value
            
    
# class to hold weekly repeat data
# repeat: days/week, days/month, days/year
class Repeat:
    cycle: RepeatCycle
    duration: RepeatDuration
    
    def __init__(self, repeat:RepeatCycle, duration: RepeatDuration):
        self.cycle = repeat
        self.duration = duration
    

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
        
    def __str__(self):
        result = "" + self.num_timespans + self.timespan_type


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
        
    # for printing
    def __str__(self):
        result = "name" + self.name + "\n"
        result += "desc: " + self.desc + "\n"
        
        result += "notifs:\n"
        for notif in self.notification_times:
            result += f"\t{notif}\n"
        
        result += "date range: " + self.date_range + "\n"
        result += "time range: " + self.time_range + "\n"
        
        result += "repeat:\n"
        result += "\ttype: " + self.repeat.cycle + "\n"
        result += "\tdur: " + self.repeat.duration + "\n"
        
        return result