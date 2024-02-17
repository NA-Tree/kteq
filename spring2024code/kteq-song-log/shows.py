#!/usr/bin/python3

import datetime
import xml.etree.ElementTree as ET

# ===========================================================================
# Show list Class
# ===========================================================================

MONDAY    = 0
TUESDAY   = 1
WEDNESDAY = 2
THURSDAY  = 3
FRIDAY    = 4
SATURDAY  = 5
SUNDAY    = 6

class Shows(object):

  def __init__(self):
    self.mon  = []
    self.tue  = []
    self.wed  = []
    self.thu  = []
    self.fri  = []
    self.sat  = []
    self.sun  = []
    self.list = []
    self.schedule = []

    # add Free Play/Unscripted to all dates
    self.mon.append("Free Play/Unscripted")
    self.tue.append("Free Play/Unscripted")
    self.wed.append("Free Play/Unscripted")
    self.thu.append("Free Play/Unscripted")
    self.fri.append("Free Play/Unscripted")
    self.sat.append("Free Play/Unscripted")
    self.sun.append("Free Play/Unscripted")

    # Gather all other shows from xml file
    tree = ET.parse('shows.xml')
    root = tree.getroot()
    for date in root:
        for show in date.findall('show'):
            for status in show.findall('status'):
                if status.text.upper() == "ACTIVE":
                    self.addShow(show.attrib['name'], date.attrib['name'])
                    # print("\t", show.attrib['name'])
                    for aka in show.findall('aka'):
                        self.addShow(aka.text, date.attrib['name'])
                        # print("\t", aka.text)

    # combine everything to full list
    self.schedule.append(self.mon)
    self.schedule.append(self.tue)
    self.schedule.append(self.wed)
    self.schedule.append(self.thu)
    self.schedule.append(self.fri)
    self.schedule.append(self.sat)
    self.schedule.append(self.sun)

    self.dayOfWeek()

  def addShow(self, show, date):
    if date == "Monday":
        self.mon.append(show)
    elif date == "Tuesday":
        self.tue.append(show)
    elif date == "Wednesday":
        self.wed.append(show)
    elif date == "Thursday":
        self.thu.append(show)
    elif date == "Friday":
        self.fri.append(show)
    elif date == "Saturday":
        self.sat.append(show)
    elif date == "Sunday":
        self.sun.append(show)


  def dayOfWeek(self):
  	#clear list
    self.list[:] = []
    day = datetime.datetime.today().weekday()
    if( day == MONDAY ):
      self.list.append(self.mon)
    elif( day == TUESDAY ):
      self.list.append(self.tue)
    elif( day == WEDNESDAY ):
      self.list.append(self.wed)
    elif( day == THURSDAY ):
      self.list.append(self.thu)
    elif( day == FRIDAY ):
      self.list.append(self.fri)
    elif( day == SATURDAY ):
      self.list.append(self.sat)
    elif( day == SUNDAY ):
      self.list.append(self.sun)

    #Collapse list
    self.list = [item for sublist in self.list for item in sublist]
  
  def printFullSchedule(self):
    print("Current KTEQ Shows: ")
    for day in self.schedule:
      for show in day:
        print(show)

  def printlistsSchedule(self):
    print("Today's Schedule: ")
    self.dayOfWeek()
    for show in self.list:
      print(show)

if __name__ == '__main__':
  s = Shows()
  s.printFullSchedule()
  print("")
  s.printlistsSchedule()  

