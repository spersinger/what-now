from CalendarEvent import CalendarEvent, DateRange, TimeRange, Repeat, NotifTime, TimeType, RepeatDuration, RepeatCycle, Day
from datetime import date as Date, time as Time, timedelta
from local_syllabus_parser import LocalSyllabusParser
from llama_cpp import Llama
import json
#re for expression recognition (used to parse date and time)
import re
from datetime import datetime

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

        self.llm = Llama(
            model_path="models/qwen2.5-coder-1.5b-instruct-q4_0.gguf",
            n_ctx=1024,  # Context window
            n_threads=10  # CPU threads

        )

    #AI model for parsing commands
    def parse_command(self, text: str) -> dict:
        prompt = f"""You are a JSON extraction assistant. Parse the following user input into structured commands.

        USER INPUT:
        {text}

        INSTRUCTIONS:
        1. Identify each command (ADD, DELETE, EDIT, SEARCH)
            - For EDIT commands use the EDIT format:
                - "target" = existing event info to find (old values)
                - "updates" = new values to apply
                    - if a value is in target do not re use it in updates (except for name)
                        - e.g., if there are two dates, use the first for target and other for updates start_date
                - Only include fields that are mentioned
            - For other commands (ADD, DELETE, SEARCH) use the STANDARD format:
                - Ignore "target" and "updates" (set them to null)
        2. Extract event name for each command (event name should be after the command)
        3. Extract a short event description:
            - Include only words that describe the event itself
            - Exclude weekdays, date, time, repeat, and notification phrases
            - null if none
        4. Extract date (natural language allowed, e.g., "monday", "dec 8")
            -start_date:
                - If the user specifies a day of the week (e.g., "monday", "tuesday"), or "tomorrow", return the day name as-is instead of a numeric date.
                - if there are two dates use the first date for start_date
            -end_date:
                -if there is only one date, use it for both start_date and end_date
                - if there is two dates use the second one for end_date
            - if the year is not mentioned, use 2026
        5. Extract start_time (e.g., "8:00 am", 8 am)
        6. Extract end_time (e.g., "8:00 am", 8 am) if present
            - if only 1 time is present, assume it is start time, and make the end time 1 hour later
        7. Extract repeat information:
            - repeat pattern (e.g., "every day", "every week", "every month" "every year") or null
            - repeat duration:
                - "forever"
                - "X times" (e.g., "5 times")
                - "until DATE" (e.g., "until dec 10")
        8. Extract notifications (e.g., "10 minutes before") as a list
        9. If information is missing, use null
        10. Output ONLY valid JSON, no explanation

        STANDARD FORMAT:
        {{
          "commands": [
            {{
              "type": "ADD|DELETE|SEARCH",
              "name": "event name",
              "description": null,
              "notifications": [],
              "date": {{
                "start_date": null,
                "end_date": null
            }},
              "start_time": "time",
              "end_time": null,
              "repeat": {{
                "pattern": null,
                "duration": null
            }},
        }}
        ]
        }}
        
        EDIT FORMAT:
        {{
        "commands": [
            {{
             "type": "EDIT",
             "target": {{
                "name": "...",
                "date": "...",
                "start_time": null
            }},
            "updates": {{
                "date": {{
                "start_date": null,
                "end_date": null
            }},
                "start_time": null,
                "end_time": null,
                "description": null,
                "notifications": [],
                "repeat": {{
                "pattern": null,
                "duration": null
                }}
              }}
            ]
            }}
            }}

        JSON:"""

        response = self.llm.create_chat_completion(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.1,
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        content = response['choices'][0]['message']['content']

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return {"error": "Failed to parse JSON"}

    #manual parsing for date
    def parse_date(self, date_str: str) -> Date:
        date_str = date_str.lower()

        weekdays = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }

        months = [
            "jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec",
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]

        # default
        event_date = Date.today()

        if date_str is None:
            return event_date
        elif re.match(r"\d{4}-\d{2}-\d{2}", date_str):
            year, month, day = map(int, date_str.split("-"))
            date_obj = Date(year, month, day)
            return date_obj
        # tomorrow
        elif "tomorrow" in date_str:
            event_date = Date.today() + timedelta(days=1)

        # weekday
        elif any(day in date_str for day in weekdays):
            for day_name, day_num in weekdays.items():
                if day_name in date_str:
                    today = Date.today()
                    today_num = today.weekday()
                    days_ahead = (day_num - today_num + 7) % 7
                    days_ahead = days_ahead if days_ahead != 0 else 7
                    event_date = today + timedelta(days=days_ahead)
                    break

        # month dd
        elif re.search(r'(' + '|'.join(months) + r')\s+\d{1,2}(\s+\d{4})?', date_str, flags=re.IGNORECASE):
            date_match = re.search(r'(' + '|'.join(months) + r')\s+\d{1,2}(\s+\d{4})?', date_str, flags=re.IGNORECASE)
            event_date = DateRange._str_to_date(date_match.group(0))

        # mm/dd
        elif re.search(r'\b\d{1,2}/\d{1,2}(/\d{2,4})?\b', date_str):
            date_match = re.search(r'\b\d{1,2}/\d{1,2}(/\d{2,4})?\b', date_str)
            event_date = DateRange._str_to_date(date_match.group(0))

        return event_date

    #manual parse for time:
    def parse_time(self, start_str: str, end_str: str = None) -> TimeRange:
        # default
        event_start = Time(12, 0)
        event_end = Time(13, 0)

        if start_str:
            time_match = re.search(r'(\d{1,2}(:\d{2})?\s*(am|pm))', start_str, flags=re.IGNORECASE)

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
                    parts = time_str.split()
                    hour_str = parts[0]
                    minute_str = "0"
                    meridiem = parts[1] if len(parts) > 1 else ""

                hour = int(hour_str)
                minute = int(minute_str)

                # convert to 24-hour
                if meridiem.lower() == "pm" and hour != 12:
                    hour += 12
                elif meridiem.lower() == "am" and hour == 12:
                    hour = 0

                event_start = Time(hour, minute)

                # handle end time
                if end_str:
                    end_match = re.search(r'(\d{1,2}(:\d{2})?\s*(am|pm))', end_str, flags=re.IGNORECASE)
                    if end_match:
                        end_time_str = end_match.group(0).strip()

                        if ":" in end_time_str:
                            h_str, rest = end_time_str.split(":")
                            if " " in rest:
                                m_str, mer = rest.split()
                            else:
                                m_str = rest
                                mer = ""
                        else:
                            parts = end_time_str.split()
                            h_str = parts[0]
                            m_str = "0"
                            mer = parts[1] if len(parts) > 1 else ""

                        h = int(h_str)
                        m = int(m_str)

                        if mer.lower() == "pm" and h != 12:
                            h += 12
                        elif mer.lower() == "am" and h == 12:
                            h = 0

                        event_end = Time(h, m)
                    else:
                        event_end = Time(hour + 1 if hour < 23 else 23, minute)

                else:
                    # default = +1 hour
                    event_end = Time(hour + 1 if hour < 23 else 23, minute)

        return TimeRange(event_start, event_end)


    #manual parse for notifications
    def parse_notifications(self, notif_list) -> list:
        notifs = []

        if not notif_list:
            return notifs

        for notif_str in notif_list:
            notif_matches = re.findall(
                r'(\d+)\s*(minute|minutes|hour|hours|day|days)\s*before',
                notif_str,
                flags=re.IGNORECASE
            )

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

                notifs.append(NotifTime(amount, timespan))

        return notifs

    #manual parse for repeat
    def parse_repeat(self, repeat_data, start,end) -> Repeat:
        # repeat_data is a dictionary from the AI model

        if repeat_data:
            pattern = repeat_data.get("pattern")
            duration = repeat_data.get("duration")
        else:
            pattern = None
            duration = None


        day_map = {
            "Monday": "m",
            "Tuesday": "t",
            "Wednesday": "w",
            "Thursday": "r",
            "Friday": "f",
            "Saturday": "s",
            "Sunday": "u"
        }

        #convert start and end to day of week
        start_dow= day_map[start.strftime("%A")]
        end_dow = day_map[end.strftime("%A")]

        ##TODO: Fix parsing for cycle and duration (LET IT BE NONE)
        # Handle cycle
        if pattern is None:
            repeat_cycle = RepeatCycle("day",start_dow )  # default
        elif pattern.lower() == "every day":
            repeat_cycle = RepeatCycle("day", start_dow)
        elif pattern.lower() == "every week":
            repeat_cycle = RepeatCycle("week", start_dow)
        elif pattern.lower() == "every month":
            repeat_cycle = RepeatCycle("month", start)
        elif pattern.lower() == "every year":
            repeat_cycle = RepeatCycle("year", start)
        else:
            repeat_cycle = RepeatCycle("day", start_dow)  # fallback

        # Handle duration
        if duration is None:
            repeat_duration = RepeatDuration("times", 0)
        elif duration.lower() == "forever":
            repeat_duration = RepeatDuration("forever", 500)
        elif "times" in duration:
            num = int(re.search(r"(\d+)", duration).group(1))
            repeat_duration = RepeatDuration("times", num)
        elif "until" in duration:
            date_str = re.search(r"until (.+)", duration).group(1)
            repeat_duration = RepeatDuration("until", end)
        else:
            repeat_duration = RepeatDuration("times", 0)  # fallback

        return Repeat(repeat_cycle, repeat_duration)

    # interpret text input and create one or more commands based on it
    # (use AI model to transform text into list of commands)
    def generate_commands(self, text:str):
        '''Receives text input
        Uses AI model to parse for each commands data
        then manual parses what the AI model returns
        appends each command to the commands list
        '''


        #AI parsing of the input
        result = self.parse_command(text)

        #for each command that the AI finds
        for cmd_data in result["commands"]:
            cmd_type = cmd_data["type"]


            if cmd_type == "ADD":

                name = cmd_data["name"]
                desc = cmd_data["description"]

                # date
                start_date = self.parse_date(cmd_data["date"]["start_date"])
                end_date = self.parse_date(cmd_data["date"]["end_date"])
                # time
                time_range = self.parse_time(
                    cmd_data["start_time"],
                    cmd_data["end_time"]
                )

                # notifications
                notifs = self.parse_notifications(cmd_data["notifications"])

                # repeat
                repeat = self.parse_repeat(cmd_data["repeat"], start_date, end_date)

                event = CalendarEvent(
                    name=name,
                    desc=desc,
                    notifs=notifs,
                    dates=DateRange(start_date,end_date),
                    times=time_range,
                    repeat=repeat
                )

                self.commands.append(Command(CommandType.ADD, event))
            elif cmd_type == "DELETE":

                name = cmd_data["name"]
                desc = cmd_data["description"]

                # date
                start_date = self.parse_date(cmd_data["date"]["start_date"])
                end_date = self.parse_date(cmd_data["date"]["end_date"])
                # time
                time_range = self.parse_time(
                    cmd_data["start_time"],
                    cmd_data["end_time"]
                )

                # notifications
                notifs = self.parse_notifications(cmd_data["notifications"])

                # repeat
                repeat = self.parse_repeat(cmd_data["repeat"], start_date, end_date)

                #for delete we should only need a name and date?
                #maybe time?
                #so what should we set description, notifs, repeat to?

                event = CalendarEvent(
                    name=name,
                    desc=desc,
                    notifs=notifs,
                    dates=DateRange(start_date,end_date),
                    times=time_range,
                    repeat=repeat #should change this to None, but it is not accepted by repeat
                )

                self.commands.append(Command(CommandType.DELETE, event))
            elif cmd_type == "SEARCH":

                name = cmd_data["name"]
                desc = cmd_data["description"]

                # date
                start_date = self.parse_date(cmd_data["date"]["start_date"])
                end_date = self.parse_date(cmd_data["date"]["end_date"])
                # time
                time_range = self.parse_time(
                    cmd_data["start_time"],
                    cmd_data["end_time"]
                )

                # notifications
                notifs = self.parse_notifications(cmd_data["notifications"])

                # repeat
                repeat = self.parse_repeat(cmd_data["repeat"], start_date, end_date)

                #for search we should only need a name and date?
                #maybe time?
                #so what should we set description, notifs, repeat to?

                event = CalendarEvent(
                    name=name,
                    desc=desc,
                    notifs=notifs,
                    dates=DateRange(start_date,end_date),
                    times=time_range,
                    repeat=repeat #should change this to None, but it is not accepted by repeat
                )

                self.commands.append(Command(CommandType.SEARCH, event))

            ##TODO: dont want to search based on a repeat, but can't be None
            # same for update, dont always want to update the repeat, but it can't be None
            # only searching based on name and date
            elif cmd_type == "EDIT":
                # name of the event to edit

                # using this for both old and new right (cant change name)
                target_name = cmd_data["target"]["name"]
                target_date = self.parse_date(cmd_data["target"]["date"]["start_date"])

                #put all update info in updates
                updates = cmd_data["updates"]

                # get all the update data or set them to null
                if updates.get("start_time") or updates.get("end_time"):
                    update_time = self.parse_time(
                        updates.get("start_time"),
                        updates.get("end_time")
                    )
                else:
                    update_time = None
                if updates.get("description"):
                    update_desc = updates.get("description")
                else:
                    update_desc = None
                if updates.get("notifications"):
                    update_notif = self.parse_notifications(updates.get("notifications"))
                else:
                    update_notif = None

                update_dates = cmd_data["updates"].get("date")

                if update_dates:
                    update_sd = self.parse_date(update_dates.get("start_date"))
                    update_ed = self.parse_date(update_dates.get("end_date"))
                else:
                    update_sd = None
                    update_ed = None

                # Create a CalendarEvent for old values to search
                search_event = CalendarEvent(
                    name=target_name,
                    desc=None,
                    notifs=[],
                    dates=DateRange(target_date,target_date),
                    times=None,
                    # repeat needs to be none, dont want to search with it
                    repeat=Repeat(RepeatCycle("day","m"),RepeatDuration("times", 0))
                )

                # Create a CalendarEvent only for the new values
                updated_event = CalendarEvent(
                    name=target_name,
                    desc=update_desc,
                    notifs=update_notif,
                    dates=DateRange(update_sd,update_ed),
                    times=update_time,
                    #repeat needs to accept None in case it doesn't need to be changed
                    repeat=Repeat(RepeatCycle("day","m"),RepeatDuration("times", 0))
                )
                # prints are just here to test the data, looking pretty good
                print(search_event)
                print(updated_event)
                self.commands.append(Command(CommandType.EDIT,data= (search_event, updated_event) ))


    #manually add command to queue
    # much faster (no AI model use)
    def add_command(self, command:Command):
        self.commands.append(command)