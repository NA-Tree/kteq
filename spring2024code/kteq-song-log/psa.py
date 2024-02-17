#!/usr/bin/python3

# ===========================================================================
# PSA List Class
# ===========================================================================

class PSA(object):

  def __init__(self):
    self.list = []
    self.list.append("Adoption from Foster Care - Breakup 60")
    self.list.append("Buzzed Driving Prevention - Drive Around 30")
    self.list.append("Child Passenger Safety - Let Me Ask You 30")
    self.list.append("Community Engagement - The Difference Is You 60")    
    self.list.append("Emergency Preparedness - Make a Plan 30")
    self.list.append("Financial Literacy - Rockstar 60")
    self.list.append("Food Safety Education - Mosh 30")
    self.list.append("Supporting Minority Education - Opportunity-Alisha 30")
    self.list.append("Teacher Recruitment - Growing Up 30")
    self.list.append("Women's Heart Disease - Breaking News 30")
    self.list.sort()

if __name__ == '__main__':
  print("Current PSAs in Rotation: ")
  p = PSA()
  for psa in p.list:
    print(psa)  
