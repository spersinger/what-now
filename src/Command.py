from CalendarEvent import CalendarEvent, DateRange, TimeRange, Repeat, NotifTime, TimeType, RepeatDuration, RepeatCycle, DurationType, Day
from datetime import date as Date, time as Time, timedelta

#re for expression recognition (used to parse date and time)
import re

from enum import Enum
from typing import Tuple, List

class CommandType(Enum):
    """Represents the different functions a Command can process."""
    
    SEARCH = 0
    EDIT = 1
    ADD = 2
    DELETE = 3



# command
# holds information about one request to send to the schedule.
class Command:
    """
    Holds information about an event and what to do with it.
    
    Command Types:
    --------------
    
    SEARCH: 
        - retrieve information about an event.
        - data is a CalendarEvent whose entries are used as search terms
        
    EDIT:
        - modify an existing event or series of events.
        - data is a pair of CalendarEvents (tuple):
            - first's fields are used as search terms (find event to modify)
            - second is what fields to modify (to leave unchanged, use None)
    
    ADD: 
        - add a new event to the schedule. 
        - data is the CalendarEvent to add (if repeating, will add all repeats).

    
    DELETE: 
        - remove an event or series of events.
        - data is a CalendarEvent whose search terms are used to find the event.
    
    """
    
    c_type: CommandType
    data: CalendarEvent | Tuple[CalendarEvent, CalendarEvent] # if 2: first is search, 2nd is modifier
    
    def __init__(self, c_type:CommandType, data:CalendarEvent|Tuple[CalendarEvent, CalendarEvent]):
        self.c_type = c_type
        self.data = data
    
    
    
# a status code from the schedule
class StatusCode(Enum):
    SUCCESS = 0
    ERROR = 0
    
    
    
# response
# holds information returned by schedule
# correlates to exactly one command
class Response:
    """Holds information about the status of a Command."""
    status: StatusCode
    status_details: str
    data = None
    
    def __init__(self):
        self.status = StatusCode.SUCCESS
        self.status_details = ""
        self.data = None
    
    
    
# command interpreter
# transforms text input into a list of commands (to eventually send to the schedule)
class CommandInterpreter:
    """Transforms text input into a series of Commands."""
    
    # commands to be sent to the schedule
    commands: List[Command]
    
    def __init__(self):
        self.commands = list()
    
    # interpret text input and create one or more commands based on it
    # (use AI model to transform text into list of commands)
    def generate_commands(self, text:str):
        '''Receives text input
        appends each command to the commands list
        '''

        text = text.lower()
        # split the input if multiple commands
        parts = text.split(" and ")

        ##TODO: replace this with AI model.

        for part in parts:
            part = part.strip()
            words = part.split()
            #defaults
            name = "event"
            event_date = Date.today()
            time_range = TimeRange(t1=Time(12, 0), t2=Time(12, 50))
            notif = []
            description = ""

            # default: single occurrence (not repeating)
            repeat_cycle = RepeatCycle("day", set())
            repeat_duration = RepeatDuration(DurationType.NUM_TIMES, 1)
            repeat_def = Repeat(repeat_cycle, repeat_duration)
            # weekday values
            weekdays = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6
            }
            # months
            months = [
                "jan", "feb", "mar", "apr", "may", "jun",
                "jul", "aug", "sep", "oct", "nov", "dec",
                "january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december"
            ]

            # get name (first word after command for now)
            for i, word in enumerate(words):
                if word in ["add", "create", "delete", "edit", "change", "find", "search"]:
                    if i + 1 < len(words):
                        name = words[i + 1]
                    break

            #getting description
            description_words = []
            # keywords that will definitley be used outside of desc
            keywords = set(["tomorrow"] + list(weekdays.keys()) + months + ["every", "day", "week", "month", "year", "at", "am","pm"])
            for word in words[i + 2:]:  # start after command + name
                if word.lower() in keywords:
                    break
                description_words.append(word)

            description = " ".join(description_words) if description_words else None

           # get date ------------------------------------
            # handle tomorrow
            if "tomorrow" in part:
                event_date = Date.today() + timedelta(days=1)
                # date range to specify when adding event to command
                date_range = DateRange(d1=event_date, d2=event_date)
            # handle days of the week
            elif any(day in part for day in weekdays):
                for day_name, day_num in weekdays.items():
                    if day_name in part:
                        today = Date.today()
                        today_num = today.weekday()  # 0 = Monday, 6 = Sunday
                        days_ahead = (day_num - today_num + 7) % 7
                        days_ahead = days_ahead if days_ahead != 0 else 7  # always next occurrence
                        event_date = today + timedelta(days=days_ahead)
                        break  # stop after first match
                # date range to specify when adding event to command
                date_range = DateRange(d1=event_date, d2=event_date)

            # handles input like "month dd"
            # search for a date string like month d or mon d
            elif re.search(r'(' + '|'.join(months) + r')\s+\d{1,2}(\s+\d{4})?', part, flags=re.IGNORECASE):
                # get the matched date string
                date_str = re.search(r'(' + '|'.join(months) + r')\s+\d{1,2}(\s+\d{4})?', part,flags=re.IGNORECASE).group(0)
                # convert to Date object
                event_date = DateRange._str_to_date(date_str)
                # create a DateRange for a single-day event
                date_range = DateRange(d1=event_date, d2=event_date)

            # handle mm/dd/yy inputs
            # search for a date string
            elif re.search(r'\b\d{1,2}/\d{1,2}(/\d{2,4})?\b', part):
                # extract the matched numeric date string
                date_str = re.search(r'\b\d{1,2}/\d{1,2}(/\d{2,4})?\b', part).group(0)
                # convert to Date object using your DateRange class
                event_date = DateRange._str_to_date(date_str)
                # create a DateRange for a single-day event
                date_range = DateRange(d1=event_date, d2=event_date)

            # End of getting date --------------------------------

            # Start of getting time ----------------------------------

            time_match = re.search(r'(\d{1,2}(:\d{2})?\s*(am|pm))', part, flags=re.IGNORECASE)
            if time_match:
                time_str = time_match.group(0).strip()

                # split into hours, minutes, meridiem
                if ":" in time_str:
                    hour_str, rest = time_str.split(":")
                    if " " in rest:
                        minute_str, meridiem = rest.split()
                    else:
                        minute_str = rest
                        meridiem = ""
                else:
                    # e.g., "8 am"
                    hour_str = time_str.split()[0]
                    minute_str = "0"
                    meridiem = time_str.split()[1]

                hour = int(hour_str)
                minute = int(minute_str)

                # convert to 24-hour Time object if needed
                if meridiem.lower() == "pm" and hour != 12:
                    hour += 12
                elif meridiem.lower() == "am" and hour == 12:
                    hour = 0

                event_start = Time(hour, minute)
                # for now, make end time 50 min later as default
                event_end = Time(hour, minute + 50 if minute + 50 < 60 else 59)
                time_range = TimeRange(t1=event_start, t2=event_end)
            # End of getting time------------------------------------------------

            # Start getting Notifications--------------------------------

            # match strings like "10 minutes before" or "1 hour before"
            notif_matches = re.findall(r'(\d+)\s*(minute|minutes|hour|hours)\s*before', part, flags=re.IGNORECASE)
            for amount, unit in notif_matches:
                amount = int(amount)
                if unit.lower().startswith("minute"):
                    timespan = TimeType.MINUTE
                elif unit.lower().startswith("hour"):
                    timespan = TimeType.HOUR
                elif unit.lower().startswith("day"):
                    timespan = TimeType.DAY
                else:
                    timespan = TimeType.MINUTE  # default

                notif.append(NotifTime(amount, timespan))
            # End getting notifications-----------------------------------

            #start getting repeat-----------------------------------------------
            if "every day" in part:
                repeat_cycle = RepeatCycle("day", set())
            elif "every week" in part:
                # look for specific weekdays mentioned
                weekdays_in_text = {day_name for day_name in weekdays if day_name in part}
                if weekdays_in_text:
                    # convert to Day enums
                    day_enum_set = set()
                    for day_name in weekdays_in_text:
                        match day_name.lower():
                            case "monday":
                                day_enum_set.add(Day.MONDAY)
                            case "tuesday":
                                day_enum_set.add(Day.TUESDAY)
                            case "wednesday":
                                day_enum_set.add(Day.WEDNESDAY)
                            case "thursday":
                                day_enum_set.add(Day.THURSDAY)
                            case "friday":
                                day_enum_set.add(Day.FRIDAY)
                            case "saturday":
                                day_enum_set.add(Day.SATURDAY)
                            case "sunday":
                                day_enum_set.add(Day.SUNDAY)
                    repeat_cycle = RepeatCycle("week", day_enum_set)
                else:
                    repeat_cycle = RepeatCycle("week", set())  # every week, no specific days

            if "forever" in part:
                repeat_duration = RepeatDuration("forever", None)

            match = re.search(r"(\d+)\s+times", part)
            if match:
                repeat_duration = RepeatDuration("times", match.group(1))

            match = re.search(r"until (\w+ \d{1,2}(?: \d{4})?)", part)
            if match:
                repeat_duration = RepeatDuration("until", match.group(1))

            # can expand later for month

            repeat_def = Repeat(repeat_cycle, repeat_duration)
            #End getting repeat--------------------------------------------------------

            if "add" in part or "create" in part:
                event = CalendarEvent(
                    name= name,
                    desc=description,
                    notifs=notif,
                    dates=date_range,
                    times=time_range,
                    repeat=repeat_def
                )
                self.commands.append(Command(c_type=CommandType.ADD, data=event))

            elif "delete" in part:
                event = CalendarEvent(
                    name=name,
                    desc=None,
                    notifs=[],
                    dates=None,
                    times=None,
                    repeat=Repeat("day", "times 1")
                )
                self.commands.append(Command(c_type=CommandType.DELETE, data=event))

            elif "edit" in part or "change" in part:
                # search for this event
                search_event = CalendarEvent(
                    name=name,
                    desc=None,
                    notifs=[],
                    dates=None,
                    times=None,
                    repeat=Repeat("day","times 1")
                )

                # What to edit (None = leave unchanged)
                edit_event = CalendarEvent(
                    name=name,
                    desc=description,
                    notifs=notif,
                    dates=date_range,
                    times=time_range,
                    repeat=repeat_def
                )
                self.commands.append(Command(c_type=CommandType.EDIT, data = (search_event,edit_event)))

            elif "search" in part or "find" in part:
                event = CalendarEvent(
                    name=name,
                    desc=None,
                    notifs=[],
                    dates=None,
                    times=None,
                    repeat=Repeat("day","times 1")
                )
                self.commands.append(Command(c_type=CommandType.SEARCH, data=event))

    # manually add command to queue
    # much faster (no AI model use)
    def add_command(self, command:Command):
        self.commands.append(command)