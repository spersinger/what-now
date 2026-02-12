from CalendarEvent import CalendarEvent
from typing import List

# contains all of a user's events
# purpose: manage calendar events
class Schedule():
    events: List[List[CalendarEvent]] # repeating events grouped together
    
    def __init__(self):
        events = []
        
    # returns a list of best matches for the given input
    # search by name, date, 
    def search_events(self, name:str=None, ) -> List[CalendarEvent]:
        pass
    
    def add_event(self, event:CalendarEvent):
        pass
