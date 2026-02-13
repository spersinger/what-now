import sys
import os
sys.path.insert(0, os.path.abspath('./src'))

from src.Schedule import *
from src.CalendarEvent import *


test = Schedule()

print("adding schedule data")
test.TEST_SET_SCHEDULE()

print("\nprinting data")
test.TEST_PRINT_SCHEDULE()