from CalendarEvent import *
from typing import List
from Command import Command, Response, CommandType, StatusCode
from kivy.clock  import Clock
from copy import deepcopy
from difflib import SequenceMatcher
import calendar
import datetime

from Notifier import Notifier

import json
import icalendar
from icalendar import Calendar, Event, Alarm
#from datetime import datetime
from datetime import date
from datetime import time
# contains all of a user's events
# purpose: manage calendar events
class Schedule():
    events: List[List[CalendarEvent]] # repeating events grouped together
    notifier: Notifier

    def __init__(self):
        # TODO: Pull events from iCal file
        self.notifier = Notifier()
        self.events = []
        #auto load events from file
        self.load_from_ics()


    # this function is called on start up to load in the ics file's events
    def load_from_ics(self,filename="user_schedule.ics"):
        events = []

        try:
            with open(filename, 'rb') as f:
                cal = Calendar.from_ical(f.read())
        except FileNotFoundError:
            print("No saved schedule found.")
            return False

        for component in cal.walk():
            # we only use VEVENT
            #other component types are not compatible
            #and will not be included in our app
            if component.name == "VEVENT":

                name = str(component.get('summary'))
                desc = component.get('description')

                start = component.get('dtstart').dt
                end = component.get('dtend').dt

                # convert back to our objects
                date_range = DateRange(start.date(), end.date())
                time_range = TimeRange(
                    Time(start.hour, start.minute),
                    Time(end.hour, end.minute)
                )

                #repeat
                repeat_rule = component.get('rrule')
                repeat = None
                if repeat_rule:
                    data = dict(repeat_rule)
                    frequency = data["FREQ"][0]
                    today = datetime.datetime.now()
                    r_timespan = None
                    r_days = None
                    d_type = None
                    d_times = None

                    # for cycle
                    if frequency == "DAILY":
                        r_timespan = "day"
                        r_days = {  # set of Day enums
                            Day.MONDAY,
                            Day.TUESDAY,
                            Day.WEDNESDAY,
                            Day.THURSDAY,
                            Day.FRIDAY,
                            Day.SATURDAY,
                            Day.SUNDAY
                        }
                    elif frequency == "WEEKLY":
                        r_timespan = "week"
                        r_days = set(self.day_mapping_reverse(d) for d in data["BYDAY"])
                    elif frequency == "MONTHLY":
                        r_timespan = "month"
                        r_date = data["BYMONTHDAY"]
                        #set a date just this month on certain day
                        # is good because it should only use the day # I believe?
                        r_days = {date(year = today.year, month = today.month, day = int(r_date))}
                    elif frequency == "YEARLY":
                        r_timespan = "year"
                        r_date = data["BYMONTHDAY"]
                        r_month = data["BYMONTH"]

                        r_days = {date(year = today.year, month = int(r_month), day = int(r_date))}

                    # for duration
                    if data.get('COUNT', [None])[0]:

                        d_type = "times"
                        d_times =int( data.get('COUNT')[0])

                    elif data.get('UNTIL',[None])[0]:
                        d_type = 'until'
                        until_dt =  data.get('UNTIL')[0]
                        if isinstance(until_dt, datetime.datetime):
                            d_times = until_dt.date()  # convert to date
                        else:
                            d_times = until_dt  # if it’s already a date

                    # if all needed variables exist - make the repeat
                    # if an incoming icalendar file does not have the
                    # appropriate rrule data, we will not use it
                    if r_timespan and r_days and d_type and d_times:
                        repeat = Repeat(
                            RepeatCycle(r_timespan, r_days),
                            RepeatDuration(d_type,d_times)
                        )

                ''' custom notifs -- trying to get rid of
                
                # notifications
                notif_times = []
                custom_notifs = component.get('WN-NOTIFS')
                if custom_notifs:
                    data = json.loads(str(custom_notifs))

                    for n in data:
                        notif = NotifTime(n["num"],TimeType[n["type"]])
                        notif_times.append(notif)
                '''
                #for notifications we need to loop over all subcomponents.
                # find each "VALARM" and convert it to our notifications
                notif_times = []
                for c in component.subcomponents:
                    if c.name == "VALARM":
                        trigger = c.get("TRIGGER")
                        num = None
                        time_type = None

                        if isinstance(trigger, timedelta):
                            # Negative timedelta for before an event
                            total_seconds = -trigger.total_seconds()  # make positive
                            if total_seconds % 604800 == 0:  # divisible by 7 days its a week
                                num = int(total_seconds // 604800)
                                time_type = TimeType.WEEK
                            elif total_seconds % 86400 == 0:  # days
                                num = int(total_seconds // 86400)
                                time_type = TimeType.DAY
                            elif total_seconds % 3600 == 0:  # hours
                                num = int(total_seconds // 3600)
                                time_type = TimeType.HOUR
                            elif total_seconds % 60 == 0:  # minutes
                                num = int(total_seconds // 60)
                                time_type = TimeType.MINUTE
                        #this shouldnt happen, but was how I originally thought it was
                        elif isinstance(trigger, str):
                            # legacy string format
                            if trigger.startswith("-PT"):
                                num = int(trigger[3:-1])
                            elif trigger.startswith("-P"):
                                num = int(trigger[2:-1])
                            letter = trigger[-1]
                            match letter:
                                case "M":
                                    time_type = TimeType.MINUTE
                                case "H":
                                    time_type = TimeType.HOUR
                                case "D":
                                    time_type = TimeType.DAY
                                case "W":
                                    time_type = TimeType.WEEK

                        if num is not None and time_type is not None:
                            notif = NotifTime(num, time_type)
                            notif_times.append(notif)

                event = CalendarEvent(
                    name=name,
                    desc=desc,
                    notifs=notif_times,
                    dates=date_range,
                    times=time_range,
                    repeat=repeat
                )

                self.add_event(event)
        #self.events = [[e] for e in events]

        return True


    def save_to_ics(self,events, filename="user_schedule.ics"):
        # cal used for the Calendar inside ics file
        cal = Calendar()

        for e in events:
            event = Event()
            event.add('summary', e.name)

            if e.description:
                event.add('description', e.description)

            # combine date + time

            start_dt = datetime.datetime.combine(
                e.date_range.start_date,
                e.time_range.start_time
            )

            end_dt = datetime.datetime.combine(
                e.date_range.end_date,
                e.time_range.end_time
            )

            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)

            # compatible repeat
            if e.repeat and e.repeat.cycle:
                cycle = e.repeat.cycle

                rrule = {}

                if cycle.timespan == TimeType.DAY:
                    rrule['freq'] = 'daily'
                elif cycle.timespan == TimeType.WEEK:
                    rrule['freq'] = 'weekly'
                    if cycle.days:
                        day_map_ical = {'m': 'MO', 't': 'TU', 'w': 'WE', 'r': 'TH', 'f': 'FR', 's': 'SA', 'u': 'SU'}
                        rrule['byday'] = [day_map_ical[self.day_mapping(d)] for d in cycle.days]

                elif cycle.timespan == TimeType.MONTH:
                    rrule['freq'] = 'monthly'
                    if cycle.days:
                        # gets the day (ex. 21) to repeat on the 21st of each month
                        rrule["bymonthday"] = cycle.days.day
                elif cycle.timespan == TimeType.YEAR:
                    rrule['freq'] = 'yearly'
                    if cycle.days:
                        #get month and day value
                        rrule["bymonth"] = cycle.days.month
                        rrule["bymonthday"] = cycle.days.day

                #duration

                if e.repeat.duration:
                    duration = e.repeat.duration
                     # If num_times or forever use count for #
                    # when we load in a "forever" repeat we will just make it
                    # num_times and 500.
                    if duration.dur_type == DurationType.NUM_TIMES or duration.dur_type == DurationType.FOREVER:
                        if isinstance(duration.value, int):
                            rrule["count"] = duration.value
                     # if until, place the date into the until
                    if duration.dur_type == DurationType.UNTIL_DATE:
                        if isinstance(duration.value, date):
                            dur_val = duration.value
                            rrule["until"] =datetime.datetime.combine(duration.value, datetime.datetime.min.time())

                event.add('rrule', rrule)


            # compatible notifications
            if e.notif_times:

                #grab each notification for the event
                for n in e.notif_times:
                    num = n.num_timespans
                    # only need the first letter for time type

                    type = n.timespan_type.name[0]

                    if type == "M":
                        trigger = timedelta(minutes=-num)
                    elif type == "H":
                        trigger = timedelta(hours=-num)
                    elif type == "D":
                        trigger = timedelta(days=-num)
                    else:
                        trigger = timedelta(hours=-num)

                        #for each notif time create an alarm ICAL property
                    # can't store multiple notifs in one alarm
                    alarm = Alarm()
                    alarm.add('action', 'DISPLAY')
                    alarm.add('trigger', trigger)

                    event.add_component(alarm)

            '''
            # THIS IS OLD, ONLY KEEPING IT FOR NOW IN CASE NEW NOTIF
            # (COMPATIBLE VERSION) DOESNT WORK
            if e.notif_times:

                notif_data = []
                for n in e.notif_times:
                    notif_data.append({
                        "num": n.num_timespans,
                        "type": n.timespan_type.name
                    })

                event.add('WN-NOTIFS', json.dumps(notif_data))
            '''
            cal.add_component(event)


        with open(filename, 'wb') as f:
            f.write(cal.to_ical())

    def day_mapping(self,d: Day) -> str:
        match d:
            case Day.MONDAY:
                return 'm'
            case Day.TUESDAY:
                return 't'
            case Day.WEDNESDAY:
                return 'w'
            case Day.THURSDAY:
                return 'r'
            case Day.FRIDAY:
                return 'f'
            case Day.SATURDAY:
                return 's'
            case Day.SUNDAY:
                return 'u'

    def day_mapping_reverse(self,d: str) -> Day:
        match d:
            case 'MO':
                return Day.MONDAY
            case 'TU':
                return Day.TUESDAY
            case 'WE':
                return Day.WEDNESDAY
            case 'TH':
                return Day.THURSDAY
            case 'FR':
                return Day.FRIDAY
            case 'SA':
                return Day.SATURDAY
            case 'SU':
                return Day.SUNDAY

    # TODO: Do we want to use this to auto save the schedule?
    def __cleanup__(self): pass
        # Save events to iCal file
        
    # returns the closest match;
    # search by name and optional date
    def search_events(self, search_term:CalendarEvent) -> Tuple[CalendarEvent, int, int]:
        name = search_term.name
        
        match: Tuple[CalendarEvent, int, int]
        
        # if no date, assume search is for whole group
        # TODO: necessary? figure out use case if so
        if search_term.date_range is None:
            print("Date range null")
            for g_idx, group in enumerate(self.events):
                if group[0].name == search_term.name:
                    return (group[0], g_idx, None)
            return None

        else:
            date = search_term.date_range.start_date # start date: search term
            
        # otherwise, find single event match
        for g_idx, group in enumerate(self.events):
            for e_idx, event in enumerate(group):
                
                name_close = SequenceMatcher(None, name, event.name).ratio() >= 0.8
                
                # if search tearm contains nothing except name, return group index (event 0)
                if search_term.date_range is None and name_close:
                    return (self.events[g_idx][0], g_idx, None)
                
                # if date matches, return that event
                if event.date_range.contains_date(search_term.date_range.start_date):
                    return (self.events[g_idx][e_idx], g_idx, e_idx)
        
        # no match found
        return None
    
    def get_for_date(self, date: Date) -> List[CalendarEvent]:
        result = []
        for group in self.events:
            for ev in group:
                if ev.date_range.contains_date(date):
                    result.append(ev)
        return result

    def get_event_counts(self, year, month) -> dict:
        counts = {}
        for group in self.events:
            for ev in group:
                for day in range(1, calendar.monthrange(year, month)[1] + 1):
                    d = Date(year, month, day)
                    if self._event_occurs_on(ev, d):
                        counts[day] = counts.get(day, 0) + 1
        return counts

    def _event_occurs_on(self, ev: CalendarEvent, d: Date) -> bool:
        return ev.date_range.contains_date(d)

    def get_days_with_events(self, year: int, month: int) -> Set[int]:
        days = set()
        for group in self.events:
            for ev in group:  # <-- iterate into the group
                for day in range(1, calendar.monthrange(year, month)[1] + 1):
                    d = Date(year, month, day)
                    if self._event_occurs_on(ev, d):
                        days.add(day)
        return days
    
    def add_event(self, event:CalendarEvent):

        # create group to hold event(s)
        group: List[CalendarEvent] = []
        num_repeats = -1
        
        # add any recurrences of the event to the group (do while)
        # (handle num_events duration case separately here)
        while True:
            group.append(deepcopy(event))
            num_repeats += 1
            if event.repeat == None:
                break
            event.date_range = event.get_next_occurrence_dates()
            if event.date_range == None:
                break
            if (event.repeat.duration.dur_type == DurationType.FOREVER or
                event.repeat.duration.dur_type == DurationType.NUM_TIMES) \
                and num_repeats == event.repeat.duration.value:
                break
        
        # append the group to the group list
        self.events.append(group)

        # schedule notifications immediately for new event(s)
        self._schedule_immediate_notifs(group)

    def _schedule_immediate_notifs(self, event_group: List[CalendarEvent]):
        now = datetime.datetime.now()
        midnight = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time(0, 0))
        seconds_to_midnight = (midnight - now).total_seconds()

        for event in event_group:
            if event.notif_times is None:
                continue
            for notif_time in event.notif_times:

                seconds_before = 0
                match notif_time.timespan_type:
                    case TimeType.MINUTE:
                        seconds_before = notif_time.num_timespans * 60
                    case TimeType.HOUR:
                        seconds_before = notif_time.num_timespans * 3600
                    case TimeType.DAY:
                        continue
                    case _:
                        continue

                event_time = datetime.datetime.combine(datetime.date.today(), event.time_range.start_time)
                notif_dt = event_time - datetime.timedelta(seconds=seconds_before)
                delay = (notif_dt - now).total_seconds()

                if 0 <= delay < seconds_to_midnight:
                    label = f"{notif_time.num_timespans} {notif_time.timespan_type.value}"
                    Clock.schedule_once(
                        lambda dt, e=event, l=label: self.notifier.send(
                            f"{e.name}",
                            f"{e.name} in {l}"
                        ),
                        delay
                    )


    
    def notify_daily(self):
        events_today = self.get_for_date(datetime.date.today())
        self.notifier.send("Daily Overview", f"You have {len(events_today)} events today.")


    def setup_notification_callbacks(self):
        def _schedule_notif(self, event, seconds_before, label):
            notif_time = datetime.datetime.combine(datetime.date.today(), event.time_range.start_time) - datetime.timedelta(seconds=seconds_before)
            delay = (notif_time - datetime.datetime.now()).total_seconds()
            if delay >= 0:
                Clock.schedule_once(
                    lambda dt, e=event, l=label: self.notifier.send(
                        f"{e.name}",
                        f"{e.name} in {l}"
                    ),
                    delay
                )

        # Schedule notifs days in advance
        for event_group in self.events:
            for event in event_group:
                if event.notif_times is not None:
                    for notif in event.notif_times:
                         if notif.timespan_type is TimeType.DAY:
                            _schedule_notif(self, event, event.notif_times.num_timespans * 86400, f"{notif.num_timespans} day(s)")

        # otherwise just schedule for current day
        events_today = self.get_for_date(datetime.date.today())
        for event in events_today:
            if event.notif_times is not None:
                for notif in event.notif_times:
                    match notif.timespan_type:
                        case TimeType.MINUTE:
                            _schedule_notif(self, event, notif.num_timespans * 60, f"{notif.num_timespans} minute(s)")
                        case TimeType.HOUR:
                            _schedule_notif(self, event, notif.num_timespans * 3600, f"{notif.num_timespans} hour(s)")
                        case _:
                            print(f"Unsupported time type: {notif.timespan_type}, skipping.")


    # leave index None to delete whole group
    def delete_event(self, group:int, index:int=None):
        if index is None:
            # delete entire group
            del self.events[group]
        else:
            # delete single event
            del self.events[group][index]



    # leave index None to modify whole group
    # (just deletes and creates a new series if group only)
    def modify_event(self, mod:CalendarEvent, group:int, index:int=None):
        
        # get copy of first event recurrence
        curr = deepcopy(self.events[group][0 if index is None else index]) # make sure we get an object, not a reference

        new_event = mod
        
        # replacements
        if new_event.name is None: new_event.name = curr.name
        if new_event.description is None: new_event.description = curr.description
        if new_event.notif_times is None: new_event.notif_times = curr.notif_times
        
        # more complicated replacements (dates, times, repeat)
        
        # TODO: handle edge cases
        # (ex. keeping event length the same when changing only one time)
        
        if new_event.date_range is None:
            new_event.date_range = curr.date_range
        else:
            if new_event.date_range.start_date is None:
                new_event.date_range.start_date = curr.date_range.start_date
            if new_event.date_range.end_date is None:
                new_event.date_range.end_date = curr.date_range.end_date

        if new_event.time_range is None:
            new_event.time_range = curr.time_range
        else:
            if new_event.time_range.start_time is None:
                new_event.time_range.start_time = curr.time_range.start_time
            if new_event.time_range.end_time is None:
                new_event.time_range.end_time = curr.time_range.end_time

        if new_event.repeat is None:
            new_event.repeat = curr.repeat
        else:
            if new_event.repeat.cycle is None:
                new_event.repeat.cycle = curr.repeat.cycle
            if new_event.repeat.duration is None:
                new_event.repeat.duration = curr.repeat.duration
        
        # replace
        if index is None: # whole group
            self.delete_event(group)
            self.add_event(new_event)
        else: # single event
            self.events[group][index] = new_event

            
    
    # performs the tasks set by the command
    # ex. create/modify/delete event
    def perform_command(self, command:Command) -> Response:
        response = Response()

        # yeah whatever we have to do this instead of 
        # just using the enums like it should be
        match command.c_type.name:
            case "SEARCH":
                # ensure correct command data
                assert type(command.data) == CalendarEvent
                
                # search based on command's calendarevent
                response.data = self.search_events(command.event)
                if response.data is not None:
                    response.status = StatusCode.SUCCESS
                    response.status_details = "found matching event."
                else:
                    response.status = StatusCode.ERROR
                    response.status_details = "could not find matching event."

            case "EDIT":
                # ensure correct command data
                assert type(command.data) == tuple and len(command.data) == 2
                
                # first: search based on first event (search terms)
                response.data = self.search_events(command.data[0])
                if response.data is None:
                    response.status = StatusCode.ERROR
                    response.status_details = "could not find matching event to modify."
                else:
                    response.status = StatusCode.SUCCESS
                    response.status_details = "found matching event to modify."
                    
                    # second: modify event based on second event (modify by)
                    self.modify_event(command.data[1], *response.data[1:])

            case "ADD":
                # TODO: error handling?
                self.add_event(command.data)
                response.status = StatusCode.SUCCESS
                response.status_details = "event was added to calendar."

            # use incides to delete
            case "DELETE":
                
                # ensure correct command data
                assert type(command.data) == CalendarEvent
                
                # part 1: find event (or group) to delete
                response.data = self.search_events(command.data)
                if response.data is None:
                    response.status = StatusCode.ERROR
                    response.status_details = "could not find matching event(s) to delete."
                else:
                    response.status = StatusCode.SUCCESS
                    response.status_details = "found event(s) to delete."
                    self.delete_event(*(response.data[1:]))

            case _:
                print("not supposed to happen")
        
        return response
        
        
        
    def __str__(self):
        result: str = ""
        for group in self.events:
            
            result += "\n\n\n------ EVENT GROUP ------\n"
            result += "total: " + str(len(group)) + " event(s)\n\n"
            for event in group:
                result += str(event) + "\n"
            
        return result

    def get_all_events(self) -> List[CalendarEvent]:
        """get all groups into a single list of events."""
        all_events = []
        for group in self.events:
            all_events.extend(group)
        return all_events

    def get_first_events(self) -> List[CalendarEvent]:
        """Return only one event per group (the first), for saving/exporting."""
        first_events = []
        for group in self.events:
            if group:  # make sure group is not empty
                first_events.append(group[0])  # first event in the group is the master
        return first_events

# TODO: try/except with error propogation instead of None/assert usage? (everywehre, not just this file)
