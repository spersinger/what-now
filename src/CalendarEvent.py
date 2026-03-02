from enum import Enum
from datetime import date as Date, time as Time, timedelta
from typing import List, Dict, Set, Tuple
from copy import deepcopy



class TimeType(Enum):
    """Reprenents a time denomination."""
    
    MINUTE = "minute(s)"
    HOUR = "hour(s)"
    DAY = "day(s)"
    WEEK = "week(s)"
    MONTH = "month(s)"
    YEAR = "year(s)"



class Day(Enum):
    """
    Represents a weekday.
    
    Triple-letters are the first three letters of the day.
    
    Single-letters are the first letter of the day, except:
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
    Holds a start and end time.
    
    Members:
        - start_time: starting time (Time)
        - end_time: ending time (Time)
    
    Requirements:
        - cannot have "p" with hours >12
    
    String constructors:
        - Time: r"1?[0-9]:[0-5][0-9][ap]"
    
    Notes:
        - if only one parameter is passed, both start and end will be set to it
        - end_time can be before start_time (ex. for events lasting multiple days)
        
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
    Holds a start and end date.
    
    Members:
        - start_date: beginning date (Date)
        - end_date: ending date (Date)
        
    Requirements:
        - end_date cannot be before start_date
    
    String constructors:
        - Date: 
            - r"1?[0-9]/[123]?[0-9]\(/[0-9]+)?"  (mm/dd(/yyyy))
            - r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) [123]?[0-9] ([0-9]+)?"  (mmm dd( yyyy))
        
    Notes:
        - when passed only one parameter, sets both start and end dates to that date.
    """
    start_date: Date
    end_date: Date
    
    # returns whether a certain date is within the range
    def contains_date(self, date:Date):
        return self.start_date <= date <= self.end_date        
    
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
# TODO: figure out what to do with this / how to implement
class Semesters:
    terms: Dict # {str, DateRange}


class RepeatCycle():
    """
    Specifies how an event repeats.
    
    Members:
        - timespan: by what timespan to repeat (TimeType)
        - days: which days to repeat on (weekly: Set[Day]; monthly/yearly: Set[Date])
        
    Requirements:
        - 
    
    String constructors:
        - timespan: r"day|week|month|year"
        - days:
            - r"[mtwrfsu]" (if weekly)
            - r"({Date} )+" (if monthly or yearly)
    """
    
    timespan: TimeType
    days: Set[Date] | Set[Day]
    
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
    Type of repeat duration.
    
    one of FOREVER, NUM_TIMES, or UNTIL_DATE
    """
    FOREVER = "forever"
    NUM_TIMES = "times"
    UNTIL_DATE = "until"



class RepeatDuration:
    """
    How long an event repeats for.
    
    Members:
        - dur_type: what kind of duration (forever/num times/until date) (RepeatDuration)
        - value: value associated with duration type (int for num_times, Date for until_date)
        
    String constructors:
        - dur_type: r"forever|times|until"
        - value: dat constructor if dur_type is until_date, otherwise int
    
    Notes:
        - for "forever" type, actually just make 500 (can't really have unlimited)
    """
    
    dur_type: DurationType
    value: int | Date
    
    def __init__(self, dur_type:DurationType|str, dur_value: int|Date|str):
        if type(dur_type) == str:
            dur_type = DurationType(dur_type)
        assert type(dur_type) == DurationType, "type checking"
        
        if type(dur_value) == str:
            match dur_type:
                case DurationType.FOREVER: dur_value = 500 # can't actually have forever
                case DurationType.NUM_TIMES: dur_value = int(dur_value)
                case DurationType.UNTIL_DATE: dur_value = DateRange._str_to_date(dur_value)
        if dur_value == None: dur_value = 500
        assert type(dur_value) == int or type(dur_value) == Date, "type checking"
        
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
    """
    Holds information about when and how an event can repeat.
    
    members:
        - cycle: when/how to repeat (RepeatCycle)
        - duration: how long to repeat for (RepeatDuration)
        
    string constructors:
        - repeat: RepeatCycle
        - duration: RepeatDuration
    """
    
    cycle: RepeatCycle
    duration: RepeatDuration

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
    """
    Holds a specific number of a specific timespan. Ex: 5 minutes
    
    members:
        - timespan_type: what time denomination (TimeType; e.g. minutes, hours, days)
        - num_timespans: how many specified denominations (int)
        
    requirements:
        - num_timespans must be >= 0 (non-negative)
    """
    
    timespan_type: TimeType
    num_timespans: int
    
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
class CalendarEvent():
    """
    Represents a single calendar event.
    
    members:
        - name: event name (string)
        - description: event description (string)
        - notif_times: list of times before event to notify user (List[NotifTime])
        - date_range: contains the event's start and end dates (DateRange)
        - time_range: contains the event's start and end times (TimeRange)
        - repeat: information about if, when, and how to repeat (Repeat)
    """
    
    name: str
    description: str
    notif_times: List[NotifTime]
    date_range: DateRange
    time_range: TimeRange
    repeat: Repeat
    
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
        self.notif_times = notifs
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
            case DurationType.FOREVER | DurationType.NUM_TIMES:
                # there will always be a next event
                difference = get_next_cycle_date(self) - self.date_range.start_date
                return DateRange(
                    self.date_range.start_date + difference,
                    self.date_range.end_date + difference
                )

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
        
    # for printing
    def __str__(self):
        result = "name: " + self.name + "\n"
        result += "desc:\n\t" + self.description.replace("\n", "\n\t") + "\n"
        
        if self.notif_times is not None:
            result += "notifs:\n"
            for notif in self.notif_times:
                result += "\t" + str(notif) + " before\n"
        
        result += "date range: " + str(self.date_range) + "\n"
        result += "time range: " + str(self.time_range) + "\n"
        
        result += str(self.repeat) + "\n\n"
        
        return result