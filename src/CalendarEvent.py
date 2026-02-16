from enum import Enum
from monthdelta import monthdelta
from datetime import date as Date, time as Time, timedelta
from typing import List, Dict, Set, Tuple
from copy import deepcopy

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
                result += str(day)[4:7] + ", "
            return result[:-2]
        elif self.type == TimeType.MONTH:
            result = "every month on days "
            for date in self.set:
                result += str(date.day) + ", "
            return result[:-2]
        else: # self.type == TimeType.YEAR
            result = "every year on "
            for date in self.set:
                result += str(date)[5:] + ", "
            return result[:-2]

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
    
    value: Tuple[int, Date] | Date | None
    """how many times or what date until"""
    
    def __init__(self, type:DurationType, value: Tuple[int, Date] | Date | None):
        self.dur_type = type
        self.value = value
        
    def __str__(self):
        match self.dur_type:
            case DurationType.FOREVER:
                return "forever"
            case DurationType.NUM_TIMES:
                return str(self.value[0]) + " time(s)"
            case DurationType.UNTIL_DATE:
                return "until " + str(self.value)
            case _:
                print("invalid duration type")
                return "ERRORRRRRRRR"
            

class Repeat:
    """repeat data for an event."""
    
    cycle: RepeatCycle
    """how the event repeats"""
    
    duration: RepeatDuration
    """how long the event repeats for"""
    
    # 2 halves: cycle, duration
    # cycle: ("day" | "week [mtwrf]" | "month 13 31" | "year 1/13 4/4")
    # duration: ("forever" | "n times" | "until 1/13/26")
    def __init__(self, repeat:str):
        pass

    def __init__(self, repeat: Tuple[str]):
        pass
    
    def __init__(self, repeat:RepeatCycle, duration: RepeatDuration):
        self.cycle = repeat
        self.duration = duration
    

class NotificationTime():
    """how long before an event to send a notification."""
    
    timespan_type: TimeType
    """time denomination (minutes, hours, etc.)"""
    
    num_timespans: int
    """number of time denominations"""
    
    def __init__(self, time: str):
        """initialize via a string. Example: \"10 hours\""""
        # parse number
        num, type = time.lower().split()
        
        # convert num to number
        num = int(num)
        
        # convert type to TimeType
        match type[:2]:
            case "mi":
                type = TimeType.MINUTE
            case "ho":
                type = TimeType.HOUR
            case "da":
                type = TimeType.DAY
            case "mo":
                type = TimeType.MONTH
            case "ye":
                type = TimeType.YEAR
            case _: 
                print("error: invalid notification time type. defaulting to minutes")
                type = TimeType.MINUTE
                
        # set values
        self.num_timespans = num
        self.timespan_type = type
                
    
    def __init__(self, num:int, type:TimeType=TimeType.MINUTE):
        if(num < 0): raise ValueError("Number of timespans must be non-negative.")
        self.num_timespans = num
        self.timespan_type = type
        
    def __setattr__(self, name, value):
        if name == "num_timespans" and value < 0:
            raise ValueError("Number of timespans must be non-negative.")
        super().__setattr__(name, value)
        
    def __str__(self):
        return str(self.num_timespans) + " " + self.timespan_type.value


# represents a calendar event, possibly repeating
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
    
    # initialize using strings
    def __init__(
        self,
        name: str,
        desc: str,
        notifs: Tuple[str] | str,
        dates: Tuple[str] | str,
        times: Tuple[str] | str,
        repeat: str
    ):
        self.name = name
        self.desc = desc
        
        # can have tuple of notifs or just one
        if type(notifs) == Tuple[str]:
            for notif in notifs:
                self.notification_times.append(NotificationTime(notif))
        else: # type(notifs) == str
            self.notification_times = [NotificationTime(notifs)]
        
        # can have 1 or 2 dates (if 1, duplicate)
        if type(dates) == Tuple[str]:
            self.date_range = DateRange(dates[0], dates[1])
        else: # type(dates) == str
            self.date_range = DateRange(dates)
        
        # same for times
        if type(times) == Tuple[str]:
            self.time_range = TimeRange(times[0], times[1])
        else: # type(times) == str
            self.time_range = TimeRange(times)
            
        self.repeat = Repeat(repeat)
    
    # initialize using full types
    def __init__(
        self, 
        name:str, 
        desc:str, 
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
                    # translate date to weekday value
                    day = Day((event_start + delta_day).weekday())
                    while day not in event.repeat.cycle.set:
                        delta_day = timedelta(delta_day.days + 1)
                        day = Day((event_start + delta_day).weekday())
                    return event_start + delta_day

                case TimeType.MONTH: # specific days per month
                    # return the smallest date after the current
                    later_dates = {
                        Date(event_start.year, event_start.month, date.day)
                        for date in event.repeat.cycle.set
                        if date.day > event_start.day
                    }
                    
                    # if none later than current, return smallest overall
                    # (first occurrence next month)
                    if len(later_dates) == 0:
                        later_dates = event.repeat.cycle.set
                        
                        # increment month for ecah date
                        new_dates: Set[Date] = set()
                        for date in later_dates:
                            year = event.date_range.start_date.year
                            month = event.date_range.start_date.month + 1
                            if month == 13:
                                month = 1
                                year += 1
                            new_dates.add(Date(year, month, date.day))
                        later_dates = new_dates
                            
                        
                    return min(later_dates)

                case TimeType.YEAR: # specific dates per year
                    # return the smallest date after the current
                    later_dates = {date for date in event.repeat.cycle.set if date > event_start}
                    
                    # if none later than current, return smallest overall
                    # (first occurrence next year)
                    if len(later_dates) == 0:
                        later_dates = set()
                        
                        # increment year for ecah date
                        for date in event.repeat.cycle.set:
                            later_dates.add(Date(date.year + 1, date.month, date.day))
                        
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
                difference = self.date_range.start_date - get_next_cycle_date(self)
                return DateRange(
                    self.date_range.start_date + difference,
                    self.date_range.end_date + difference
                )

            case DurationType.NUM_TIMES:
                num_repeats = self.repeat.duration.value[0]
                original_date: Date = self.repeat.duration.value[1]
                
                # emulate original event to calculate last date with
                copy: CalendarEvent = deepcopy(self)
                copy.date_range.start_date = original_date
                
                # calculate the date of the last event
                for i in range(num_repeats):
                    copy.date_range.start_date = get_next_cycle_date(copy)
                    
                last_date = copy.date_range.start_date
                
                # if current date is before last date, can safely return next iteration date
                if self.date_range.start_date < last_date:
                    difference = get_next_cycle_date(self) - self.date_range.start_date
                    return DateRange(
                        self.date_range.start_date + difference,
                        self.date_range.end_date + difference
                    )
                else:
                    return None
                

            case DurationType.UNTIL_DATE:
                difference = get_next_cycle_date(self) - self.date_range.start_date
                if self.date_range.start_date + difference > self.repeat.duration.value:
                    return None
                return DateRange(
                    self.date_range.start_date + difference,
                    self.date_range.end_date + difference
                )
            
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
                result += "\t" + str(notif) + " before\n"
        
        result += "date range: " + str(self.date_range) + "\n"
        result += "time range: " + str(self.time_range) + "\n"
        
        result += "repeat:\n"
        result += "\ttype: " + str(self.repeat.cycle) + "\n"
        result += "\tdur: " + str(self.repeat.duration) + "\n"
        
        return result