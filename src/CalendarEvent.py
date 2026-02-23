from enum import Enum
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
    
    @staticmethod
    def _str_to_time(string: str) -> Time:
        hours, minutes = string.split(":")
        assert len(minutes) == 3, "force use of ampm symbol"
        
        ampm = minutes[-1]
        assert ampm == 'a' or ampm == 'p', "must have am/pm symbol at end"
        
        minutes = int(minutes[:-1])
        hours = int(hours)
        assert type(hours) == int, "type checking"
        assert type(minutes) == int, "type checking"
        
        if hours == 12:
            if ampm == 'a': hours -= 12 # 12am; 00:00
            else: pass # 12pm; 12:00 (do nothing)
        else:
            if ampm == 'p': hours += 12 # ex. 1:00p -> 13:00
            
        assert 0 <= hours <= 23, "hours must be 0-23"
        assert 0 <= minutes <= 59, "minutes must be 0-59"

        return Time(hours, minutes)
    
    def __init__(self, t1:Time|str, t2:Time|str=None):
        if type(t1) == str:
            t1 = self._str_to_time(t1)
        assert type(t1) == Time, "type checking"
            
        if type(t2) == str:
            t2 = self._str_to_time(t2)
        assert type(t2) == Time or t2 == None, "type checking"
        
        self.start_time = t1
        self.end_time = t2 if t2 is not None else t1
        
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
    
    @staticmethod
    def _str_to_date(string: str) -> Date:
        
        split_slash = string.count("/")
        assert 0 <= split_slash <= 2, "full dates have a maximum of 2 slashes (ex. 12/31/2026)"
        
        if split_slash > 0:
            # mm/dd[/yyyy]
            
            if split_slash == 2:
                month, day, year = string.split("/")
            else:
                month, day = string.split("/")
                year = Date.today().year
        
        else: # words, ex. "jan 1 [2026]"
            num_items = len(string.split())
            
            assert 2 <= num_items <= 3, "full dates hav a maximum of 3 words (ex. dec 31 2026) "
            
            if num_items == 3:
                month, day, year = string.split()
            else: # num_items == 2
                year = Date.today().year
                month, day = string.split()
            
            match month.lower():
                case "jan": month = 1
                case "feb": month = 2
                case "mar": month = 3
                case "apr": month = 4
                case "may": month = 5
                case "jun": month = 6
                case "jul": month = 7
                case "aug": month = 8
                case "sep": month = 9
                case "oct": month = 10
                case "nov": month = 11
                case "dec": month = 12
            
        month = int(month)
        day = int(day)
        year = int(year)
        
        assert type(month) == int and 1 <= month <= 12, "type checking, value checking"
        assert type(day) == int and 1 <= day <= 31, "type checking, value checking"
        assert type(year) == int, "type checking"
        
        return Date(year, month, day)
            
    
    def __init__(self, d1:Date|str, d2:Date|str=None):
        if type(d1) == str:
            d1 = self._str_to_date(d1)
        assert type(d1) == Date, "type checking"
            
        if type(d2) == str:
            d2 = self._str_to_date(d2)
        assert type(d2) == Date or d2 == None, "type checking"
        
        self.start_date = d1
        self.end_date = d2 if d2 is not None else d1
    
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
    
    timespan: TimeType
    """by what timespan to repeat (daily, weekly, monthly, or yearly)"""
    
    days: Set[Date] | Set[Day]
    """which specific days (weekly) or dates (monthly/yearly) to repeat on"""
    
    @staticmethod
    def _str_to_time_type(string: str) -> TimeType:
        match string.lower():
            case "day": return TimeType.DAY
            case "week": return TimeType.WEEK
            case "month": return TimeType.MONTH
            case "year": return TimeType.YEAR
            case default: raise ValueError("invalid cycle type string")
    
    @staticmethod
    def _str_to_days(string: str) -> Set[Day]:
        # single-letter: "mtwrfsu"
        assert len(string) <= 7, "there are only 7 days in a week"
        assert string.find(" ") == -1, "no spaces between the specified weekdays"
        
        s: Set[Day] = set()
        
        for char in string:
            match char:
                case 'm': s.add(Day.M)
                case 't': s.add(Day.T)
                case 'w': s.add(Day.W)
                case 'r': s.add(Day.R)
                case 'f': s.add(Day.F)
                case 's': s.add(Day.S)
                case 'u': s.add(Day.U)
                case default: assert False, "days in cycle week specification must be m/t/w/r/f/s/u"
        
        return s

    @staticmethod
    def _str_to_dates(string: str) -> Set[Date]:
        # format: [month]/[day] separated by spaces
        s: Set[Date] = set()
        for date in string.split():
            s.add(DateRange._str_to_date(date))
        return s
    
    def __init__(self, timespan:TimeType|str, days: Set[Date]|Set[Day]|str):
        if type(timespan) == str:
            timespan = self._str_to_time_type(timespan)
        assert type(timespan) == TimeType, "type checking"
        
        if type(days) == str:
            if timespan == TimeType.DAY:
                days = None
            elif timespan == TimeType.WEEK:
                days = self._str_to_days(days)
            else:
                days = self._str_to_dates(days)
        assert type(days) == set or days == None, "type checking"
        
        self.timespan = timespan
        self.days = days

    def __str__(self):
        if self.timespan == TimeType.DAY:
            return "every day"
        elif self.timespan == TimeType.WEEK:
            result = "every "
            for day in self.days:
                result += str(day)[4:7] + ", "
            return result[:-2]
        elif self.timespan == TimeType.MONTH:
            result = "every month on days "
            for date in self.days:
                result += str(date.day) + ", "
            return result[:-2]
        else: # self.timespan == TimeType.YEAR
            result = "every year on "
            for date in self.days:
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
    
    value: int | Date
    """how many times or what date until"""
    
    def __init__(self, dur_type:DurationType|str, dur_value: int|Date|str):
        if type(dur_type) == str:
            dur_type = DurationType(dur_type)
        assert type(dur_type) == DurationType, "type checking"
        
        if type(dur_value) == str:
            match dur_type:
                case DurationType.FOREVER: dur_value = None
                case DurationType.NUM_TIMES: dur_value = int(dur_value)
                case DurationType.UNTIL_DATE: dur_value = DateRange._str_to_date(dur_value)
        assert type(dur_value) == int or type(dur_value) == Date or dur_value == None, "type checking"
        
        self.dur_type = dur_type
        self.value = dur_value
        
    def __str__(self):
        match self.dur_type:
            case DurationType.FOREVER:
                return "forever"
            case DurationType.NUM_TIMES:
                return str(self.value) + " time(s)"
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

    def __init__(self, repeat:RepeatCycle|str, duration: RepeatDuration|str):
        if type(repeat) == str:
            if repeat.count(" ") == 0:
                repeat = RepeatCycle(repeat, None)
            else:
                repeat = RepeatCycle(repeat[0:repeat.find(" ")], repeat[repeat.find(" ")+1:])
            
            assert type(repeat) == RepeatCycle, "type checking"
            
        if type(duration) == str:
            if duration.count(" ") == 0:
                duration = RepeatDuration(duration, None)
            else:
                duration = RepeatDuration(*duration.split())
            assert type(duration) == RepeatDuration, "type checking"
        
        self.cycle = repeat
        self.duration = duration
        
    def __str__(self):
        return "repeat: " + str(self.cycle) + ", " + str(self.duration)
    

class NotifTime():
    """how long before an event to send a notification."""
    
    timespan_type: TimeType
    """time denomination (minutes, hours, etc.)"""
    
    num_timespans: int
    """number of time denominations"""
    
    def __init__(self, num:int, type:TimeType=TimeType.MINUTE):
        
        assert num >= 0, "cannot have negative number of notif timespans"
        
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
    notification_times: List[NotifTime]
    """list of times by which to send out a notification."""
    
    date_range: DateRange
    """start and end dates"""
    
    time_range: TimeRange
    """start and end times"""
    
    repeat: Repeat
    """how and how long by which the event repeats"""
    
    # initialize using full types
    def __init__(
        self, 
        name:str, 
        desc:str, 
        notifs:List[NotifTime]|None,
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
            
            match event.repeat.cycle.timespan:
                case TimeType.DAY: # repeat every day
                    return event_start + delta_day

                case TimeType.WEEK: # repeat specific days per week
                    # translate date to weekday value
                    day = Day((event_start + delta_day).weekday())
                    while day not in event.repeat.cycle.days:
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
                # handled by Schedule (can't get last event iteratively (without original date))
                pass
                

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