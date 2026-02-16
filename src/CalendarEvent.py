from enum import Enum
from monthdelta import monthdelta
from datetime import date as Date, time as Time, timedelta
from typing import List, Dict, Set

# represents different timespan derivatives
class TimeType(Enum):
    """reprenents a time denomination."""
    
    MINUTE = "minute(s)"
    HOUR = "hour(s)"
    DAY = "day(s)"
    WEEK = "week(s)"
    MONTH = "month(s)"
    YEAR = "year(s)"

class Day(Enum):
    """
    represents a weekday.
    
    triple-letters are the first three letters of the day.
    
    single-letters are the first letter of the day, except:
        U (for Sunday)
        R (for Thursday)
    """
    
    MONDAY    = MON = M = 0
    TUESDAY   = TUE = T = 1
    WEDNESDAY = WED = W = 2
    THURSDAY  = THU = R = 3
    FRIDAY    = FRI = F = 4
    SATURDAY  = SAT = S = 5
    SUNDAY    = SUN = U = 6

# holds a single range of times
class TimeRange:
    """
    holds a start and end time.
    
    times can be the same (representing one instant, ex. for a reminder).
    
    end time can be "before" end time (for multi-day events).
        
    """
    start_time: Time
    end_time: Time
    
    def __init__(self, t1:Time, t2:Time):
        self.start_time = t1
        self.end_time = t2
        
    def __str__(self):
        return str(self.start_time) + " -> " + str(self.end_time)

# class that holds a range of dates
class DateRange:
    """
    holds a start and end date.
    
    dates can be the same (represeting a single-day event).
    """
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

# specifies amount of repeats.
# type: one of:
#       - TimeType.DAY (repeat every day)
#       - TimeType.WEEK (repeat every week on specific weekdays)
#       - TimeType.MOTNH (repeat every month on specific dates)
#       - TimeType.YEAR (repeat every year on specific dates)
# set: set of days the event will repeat on.
#       - if type==WEEK: set of weekdays
#       - else: set of Dates (if months, always use january)
class RepeatCycle():
    """specifies how an event repeats."""
    
    type: TimeType
    """by what timespan to repeat (daily, weekly, monthly, or yearly)"""
    
    set: Set[Date] | Set[Day]
    """which specific days (weekly) or dates (monthly/yearly) to repeat on"""
    
    def __init__(self, type:TimeType, set: Set[Date] | Set[Day]):
        self.type = type
        self.set = set
    
    def __str__(self):
        if self.type == TimeType.DAY:
            return "every day"
        elif self.type == TimeType.WEEK:
            result = "every "
            for day in self.set:
                result += str(day) + ", "
            return result
        elif self.type == TimeType.MONTH:
            result = "every month on days "
            for date in self.set:
                result += str(date.day) + ", "
            return result
        else: # self.type == TimeType.YEAR
            return "every year on " + (str(date) + ", " for date in self.set)

class DurationType(Enum):
    """
    type of repeat duration.
    
    one of FOREVER, NUM_TIMES, or UNTIL_DATE
    """
    FOREVER = "forever"
    NUM_TIMES = "times"
    UNTIL_DATE = "until"

class RepeatDuration:
    """repeat duration and amount."""
    
    dur_type: DurationType
    """type of duration (forever, number of times, or until specific date)"""
    
    value: int | Date | None
    """how many times or what date until"""
    
    def __init__(self, type:DurationType, value: int | Date | None):
        self.dur_type = type
        self.value = value
        
    def __str__(self):
        if self.value is None:
            return "once"
        elif type(self.value) is int:
            return str(self.value) + " times"
        else: # type(self.value) is Date
            return "until " + self.value
            

class Repeat:
    """repeat data for an event."""
    
    cycle: RepeatCycle
    """how the event repeats"""
    
    duration: RepeatDuration
    """how long the event repeats for"""
    
    def __init__(self, repeat:RepeatCycle, duration: RepeatDuration):
        self.cycle = repeat
        self.duration = duration
    

class NotificationTime():
    """how long before an event to send a notification."""
    
    timespan_type: TimeType
    """time denomination (minutes, hours, etc.)"""
    
    num_timespans: int
    """number of time denominations"""
    
    def __init__(self, num:int, type:TimeType=TimeType.MINUTE):
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
# TODO: simplify? allow data to be set with strings for convenience
#       - notif_times: string* (0 or more) ex. "1 hour", "3 minutes"
#       - date_range: 
#           - tuple(Date, Date) ex. (Date(2026, 12, 23), Date(2026, 12, 24))
#           - Date (same start/end date)
#           - string+ (1 or 2) ex. "12/23", "12/24" ("mm/dd/yyyy" only)
#       - time_range:
#           - tuple(Time, Time)
#           - Time (same start/end time)
#           - string+ (1 or 2) ex. "13:00", "13:50"
#       - repeat:
#           - string ex. "every 2 days" or "every week umtwrfs" or "every month 12,13,14" or "every year 12/13,12/14,12/15"
class CalendarEvent():
    """represents a single calendar event."""
    
    name: str
    description: str
    notification_times: List[NotificationTime]
    """list of times by which to send out a notification."""
    
    date_range: DateRange
    """start and end dates"""
    
    time_range: TimeRange
    """start and end times"""
    
    repeat: Repeat
    """how and how long by which the event repeats"""
    
    
    def __init__(
                self, 
                name:str, 
                desc:str|None, 
                notifs:List[NotificationTime]|None,
                dates: DateRange,
                times: TimeRange,
                repeat: Repeat
            ):
        self.name = name
        self.description = desc
        self.notification_times = notifs
        self.date_range = dates
        self.time_range = times
        self.repeat = repeat
        
    def get_next_occurrence_dates(self) -> DateRange | None:
        """if a repeating event, get the next occurrence. Returns None if last occurrence."""
        
        # helper to avoid repeated code
        def get_next_cycle_date(event: CalendarEvent) -> Date | None:
            """returns the would-be next event (if repeating)."""
            
            event_start: Date = event.date_range.start_date
            delta_day = timedelta(1) # time delta for incrementing days
            
            match event.repeat.cycle.type:
                case TimeType.DAY: # repeat every day
                    return event_start + delta_day

                case TimeType.WEEK: # repeat specific days per week
                    while (event_start + delta_day) % 7 not in event.repeat.cycle.set:
                        delta_day.days += 1
                    return event_start + delta_day
 
                case TimeType.MONTH: # specific days per month
                    # return the smallest date after the current
                    later_dates = {date for date in event.repeat.cycle.set if date.day > event_start.day}
                    
                    # if none later than current, return smallest overall
                    # (first occurrence next month)
                    if len(later_dates) == 0:
                        later_dates = event.repeat.cycle.set
                        
                        # increment month for ecah date
                        for date in later_dates:
                            date += monthdelta(1)
                        
                    return min(later_dates)

                case TimeType.YEAR: # specific dates per year
                    # return the smallest date after the current
                    later_dates = {date for date in event.repeat.cycle.set if date > event_start}
                    
                    # if none later than current, return smallest overall
                    # (first occurrence next year)
                    if len(later_dates) == 0:
                        later_dates = event.repeat.cycle.set
                        
                        # increment year for ecah date
                        for date in later_dates:
                            date.year += 1
                        
                    return min(later_dates)

                case _:
                    return None
        
        # guard clause: return None if not a repeating event (repeat=num_times, val=0)
        if self.repeat.duration == DurationType.NUM_TIMES and self.repeat.duration.value == 0:
            return None
        
        # duration: forever, num times, until_date
        # for each type, get the next event based on cycle
        match self.repeat.duration.dur_type:
            case DurationType.FOREVER:
                # there will always be a next event
                pass

            case DurationType.NUM_TIMES:
                pass

            case DurationType.UNTIL_DATE:
                pass
            
            case _:
                print("error: invalid duration type")
    
    def is_last_occurrence(self) -> bool:
        """if a repeating event, determine whether this one is the last occurrence."""
        return self.get_next_occurrence_dates() == None
        
    # for printing
    def __str__(self):
        result = "name: " + self.name + "\n"
        result += "desc: " + self.description + "\n"
        
        if self.notification_times is not None:
            result += "notifs:\n"
            for notif in self.notification_times:
                result += f"\t{notif}\n"
        
        result += "date range: " + str(self.date_range) + "\n"
        result += "time range: " + str(self.time_range) + "\n"
        
        result += "repeat:\n"
        result += "\ttype: " + str(self.repeat.cycle) + "\n"
        result += "\tdur: " + str(self.repeat.duration) + "\n"
        
        return result