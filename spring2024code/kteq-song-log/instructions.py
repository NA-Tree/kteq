#!/usr/bin/python3

# ===========================================================================
# Logger Instructions class
# ===========================================================================

class Instructions(object):

  def __init__(self):
    #If you need to change any of these, do it here I guess. I don't care.
    self.show = 'Please select your show from the drop down list at the '
    self.show = self.show + 'start of your program. Leave your show name '
    self.show = self.show + 'selected until you are finished.' 

    self.id = 'At the top of every hour, click the Log ID button. Make '
    self.id = self.id + 'sure you also state our station tag on air! '
    self.id = self.id + '(KTEQ FM Rapid City)' 

    self.song = 'Enter Song Name, Artist, and Composer (if applicable) '
    self.song = self.song + 'for EVERY song you play. Try to update this '
    self.song = self.song + 'in real time, as this will update the song '
    self.song = self.song + 'info metadata for listeners on TuneIn, VLC, etc.'

    self.psa = 'Twice per hour, either read or play one of the following '
    self.psa = self.psa + 'Public Service Announcements. Log the PSA '
    self.psa = self.psa + 'by selecting the correct one from the menu.'

if __name__ == '__main__':
  i = Instructions()

  print("")
  print("Show Logging Instructions: ")
  print(i.show)
  print("")

  print("")
  print("Station ID Logging Instructions: ")
  print(i.id) 
  print("")

  print("")
  print("Song Logging Instructions: ")
  print(i.song) 
  print("")

  print("")
  print("PSA Logging Instructions: ")
  print(i.psa) 
  print("")


