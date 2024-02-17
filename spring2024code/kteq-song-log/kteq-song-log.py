#!/usr/bin/python3

from tkinter import *
from tkinter import ttk
import csv
import datetime
from PIL import ImageTk, Image

#imports
import shows
import psa
import instructions

LOG_ID   = 0
LOG_SONG = 1
LOG_PSA  = 2

def logSong(*args):
	song     = songName.get()
	artist   = songArtist.get()
	composer = songComposer.get()
	show     = showName.get()
	now      = datetime.datetime.now()

	filename = 'bmi_' + str(now.month).zfill(2) + '_' + str(now.year) + '.csv'
	date = str(now.month).zfill(2) + '/' + str(now.day).zfill(2) + '/' + str(now.year)
	time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)

	with open(filename, 'a', newline='') as songlog:
		songwriter = csv.writer(songlog, delimiter=',')
		songwriter.writerow([date, time, song, artist, composer, show])

	#log to nowPlaying.txt
	nowPlaying(source=LOG_SONG)

	#update ticker
	updateTicker(source=LOG_SONG)

	#clear everything for next submission
	songName_entry.delete(0, 'end')
	songArtist_entry.delete(0, 'end')
	songComposer_entry.delete(0, 'end')

def logID():
	show = showName.get()
	now = datetime.datetime.now()
	
	filename = 'bmi_' + str(now.month).zfill(2) + '_' + str(now.year) + '.csv'
	date = str(now.month).zfill(2) + '/' + str(now.day).zfill(2) + '/' + str(now.year)
	time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)

	with open(filename, 'a', newline='') as idlog:
		idwriter = csv.writer(idlog, delimiter=',')
		idwriter.writerow([date, time, 'STATION TAG', 'KTEQ', '', show])
	
	#log to nowPlaying.txt
	nowPlaying(source=LOG_ID)

	#update ticker
	updateTicker(source=LOG_ID)


def logPSA(*args):
	show = showName.get()
	psa  = psaName.get()
	now = datetime.datetime.now()
	
	filename  = 'bmi_' + str(now.month).zfill(2) + '_' + str(now.year) + '.csv'
	filename2 = 'psa_' + str(now.month).zfill(2) + '_' + str(now.year) + '.csv'
	date = str(now.month).zfill(2) + '/' + str(now.day).zfill(2) + '/' + str(now.year)
	time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)

	with open(filename, 'a', newline='') as psalog:
		psawriter = csv.writer(psalog, delimiter=',')
		psawriter.writerow([date, time, psa, 'PSA', '', show])

	with open(filename2, 'a', newline='') as psalog:
		psawriter = csv.writer(psalog, delimiter=',')
		psawriter.writerow([date, time, psa])
	
	#log to nowPlaying.txt
	nowPlaying(source=LOG_PSA)

	#update ticker
	updateTicker(source=LOG_PSA)

def updateTicker(source=LOG_ID):
	
	song     = songName.get()
	artist   = songArtist.get()
	composer = songComposer.get()
	show     = showName.get()
	now      = datetime.datetime.now()
	psa      = psaName.get()
	date = str(now.month).zfill(2) + '/' + str(now.day).zfill(2) + '/' + str(now.year)
	time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)

	prevSong5date_lbl.config(    text=prevSong4date_lbl.cget("text"))
	prevSong5time_lbl.config(    text=prevSong4time_lbl.cget("text"))
	prevSong5title_lbl.config(   text=prevSong4title_lbl.cget("text"))
	prevSong5artist_lbl.config(  text=prevSong4artist_lbl.cget("text"))
	prevSong5composer_lbl.config(text=prevSong4composer_lbl.cget("text"))
	prevSong5show_lbl.config(    text=prevSong4show_lbl.cget("text"))

	prevSong4date_lbl.config(    text=prevSong3date_lbl.cget("text"))
	prevSong4time_lbl.config(    text=prevSong3time_lbl.cget("text"))
	prevSong4title_lbl.config(   text=prevSong3title_lbl.cget("text"))
	prevSong4artist_lbl.config(  text=prevSong3artist_lbl.cget("text"))
	prevSong4composer_lbl.config(text=prevSong3composer_lbl.cget("text"))
	prevSong4show_lbl.config(    text=prevSong3show_lbl.cget("text"))

	prevSong3date_lbl.config(    text=prevSong2date_lbl.cget("text"))
	prevSong3time_lbl.config(    text=prevSong2time_lbl.cget("text"))
	prevSong3title_lbl.config(   text=prevSong2title_lbl.cget("text"))
	prevSong3artist_lbl.config(  text=prevSong2artist_lbl.cget("text"))
	prevSong3composer_lbl.config(text=prevSong2composer_lbl.cget("text"))
	prevSong3show_lbl.config(    text=prevSong2show_lbl.cget("text"))

	prevSong2date_lbl.config(    text=prevSong1date_lbl.cget("text"))
	prevSong2time_lbl.config(    text=prevSong1time_lbl.cget("text"))
	prevSong2title_lbl.config(   text=prevSong1title_lbl.cget("text"))
	prevSong2artist_lbl.config(  text=prevSong1artist_lbl.cget("text"))
	prevSong2composer_lbl.config(text=prevSong1composer_lbl.cget("text"))
	prevSong2show_lbl.config(    text=prevSong1show_lbl.cget("text"))


	if(source==LOG_ID):
		prevSong1date_lbl.config(    text=date)
		prevSong1time_lbl.config(    text=time)
		prevSong1title_lbl.config(   text="STATION TAG")
		prevSong1artist_lbl.config(  text="KTEQ")
		prevSong1composer_lbl.config(text="")
		prevSong1show_lbl.config(    text=show)
	elif(source==LOG_SONG):
		prevSong1date_lbl.config(    text=date)
		prevSong1time_lbl.config(    text=time)
		prevSong1title_lbl.config(   text=song)
		prevSong1artist_lbl.config(  text=artist)
		prevSong1composer_lbl.config(text=composer)
		prevSong1show_lbl.config(    text=show)
	elif(source==LOG_PSA):
		prevSong1date_lbl.config(    text=date)
		prevSong1time_lbl.config(    text=time)
		prevSong1title_lbl.config(   text=psa)
		prevSong1artist_lbl.config(  text="PSA")
		prevSong1composer_lbl.config(text="")
		prevSong1show_lbl.config(    text=show)


def nowPlaying( source=LOG_ID ):
	
	#Write to a file what song is currently playing (or what have you)
	filename = 'nowPlaying.txt'
	song     = songName.get()
	artist   = songArtist.get()
	psa      = psaName.get()
	nowPlay  = open(filename, 'w')
	default = "KTEQ FM 91.3 Rapid City, South Dakota"
	if(source==LOG_ID):
		#Station ID
		line = default
	elif(source==LOG_SONG):
		#SONG
		if(song!='' and artist!=''):
			line = song + ' __by__ ' + artist
		else:
			line = default
	elif(source==LOG_PSA):
		#PSA
		if(psa!=''):
			line = psa + ' - Public Service Announcement'
		else:
			line = default
	nowPlay.write(line)

def refreshShowList():
	showName.set('')
	showList = None
	showList = shows.Shows()
	
	showName.set(showList.list[0])
	showNameList['menu'].delete(0, 'end')
	for show in showList.list:
		showNameList['menu'].add_command(label=show, command=lambda s=show: showName.set(s))
	

#create the window and title it
root = Tk()
root.title("KTEQ 91.3FM SONG AND PSA LOG")
root.resizable(FALSE,FALSE)
#create the frames
infoFrame = ttk.Frame(root, borderwidth=5, relief="sunken")
songFrame = ttk.Frame(root, borderwidth=5, relief="sunken")
psaFrame  = ttk.Frame(root, borderwidth=5, relief="sunken")
idFrame   = ttk.Frame(root, borderwidth=5, relief="sunken")
tickFrame = ttk.Frame(root, borderwidth=5, relief="sunken")
logoFrame = ttk.Frame(root, borderwidth=5, relief="sunken")

#place frames
infoFrame.grid(column=0,  row=0,  columnspan=6,  rowspan=5,  sticky=(N, W, E, S))
songFrame.grid(column=0,  row=5,  columnspan=6,  rowspan=5,  sticky=(N, W, E, S))
psaFrame.grid( column=6,  row=5,  columnspan=6,  rowspan=5,  sticky=(N, W, E, S))
idFrame.grid(  column=6,  row=0,  columnspan=6,  rowspan=5,  sticky=(N, W, E, S))
tickFrame.grid(column=0,  row=10, columnspan=18, rowspan=5,  sticky=(N, W, E, S))
logoFrame.grid(column=12, row=0,  columnspan=6,  rowspan=10, sticky=(N, W, E, S))

#CREATE NEW INSTANCE OF SHOWS AND PSAS
showList = shows.Shows()
psas = psa.PSA()
instructions = instructions.Instructions()

#Create the variables
showName = StringVar()
showName.set(showList.list[0])

psaName = StringVar()
psaName.set(psas.list[0])

songName     = StringVar()
songArtist   = StringVar()
songComposer = StringVar()


#Create text boxes
songName_entry     = ttk.Entry(songFrame, width=7, textvariable=songName)
songArtist_entry   = ttk.Entry(songFrame, width=7, textvariable=songArtist)
songComposer_entry = ttk.Entry(songFrame, width=7, textvariable=songComposer)

#Create image
img_logo = ImageTk.PhotoImage(file="img/kteq-logo.jpg")

#Place Text Boxes
songComposer_entry.grid(column=3, row=3, columnspan=6, sticky=(W, E))
songArtist_entry.grid(  column=3, row=2, columnspan=6, sticky=(W, E))
songName_entry.grid(    column=3, row=1, columnspan=6, sticky=(W, E))


#Create drop downs
showNameList = OptionMenu(infoFrame, showName, *showList.list)
psaNameList  = OptionMenu(psaFrame, psaName, *psas.list)

#Place Drop Downs
showNameList.grid(column=3, row=1, sticky=(W, E))
psaNameList.grid(column=3, row=1, columnspan=3, sticky=(W, E))

#Create buttons
logSong      = ttk.Button(songFrame, text="Log Song",     command=logSong)
logPSA       = ttk.Button(psaFrame,  text="Log PSA",      command=logPSA)
logID        = ttk.Button(idFrame,   text="Log ID",       command=logID)
refreshShows = ttk.Button(infoFrame, text="Refresh List", command=refreshShowList)

#Create Image
imgLogo = ttk.Label(logoFrame, image=img_logo)

#place buttons
logSong.grid(     column=2, row=4, sticky=(W, E))
logPSA.grid(      column=2, row=3, sticky=(W, E))
logID.grid(       column=2, row=3, sticky=(N, W, E, S))
refreshShows.grid(column=2, row=1, sticky=(N, W, E, S))

#Place Image
imgLogo.grid(column=2, row=3, sticky=(N, W, E, S))


#Create labels
songName_lbl     = ttk.Label(songFrame, text="Song Name:")
songArtist_lbl   = ttk.Label(songFrame, text="Song Artist:")
songComposer_lbl = ttk.Label(songFrame, text="Song Composer:")
psa_lbl          = ttk.Label(psaFrame,  text="PSA Title:")

#Create instructions labels
howTo_Show_lbl = ttk.Label(infoFrame, text=instructions.show, wraplength=400)
howTo_Song_lbl = ttk.Label(songFrame, text=instructions.song, wraplength=400)
howTo_ID_lbl   = ttk.Label(idFrame,   text=instructions.id  , wraplength=400)
howTo_PSA_lbl  = ttk.Label(psaFrame,  text=instructions.psa , wraplength=400)


#Labels for ticker
prevSong1date_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong1time_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong1title_lbl    = ttk.Label(tickFrame, padding=6, text="")
prevSong1artist_lbl   = ttk.Label(tickFrame, padding=6, text="")
prevSong1composer_lbl = ttk.Label(tickFrame, padding=6, text="")
prevSong1show_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong2date_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong2time_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong2title_lbl    = ttk.Label(tickFrame, padding=6, text="")
prevSong2artist_lbl   = ttk.Label(tickFrame, padding=6, text="")
prevSong2composer_lbl = ttk.Label(tickFrame, padding=6, text="")
prevSong2show_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong3date_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong3time_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong3title_lbl    = ttk.Label(tickFrame, padding=6, text="")
prevSong3artist_lbl   = ttk.Label(tickFrame, padding=6, text="")
prevSong3composer_lbl = ttk.Label(tickFrame, padding=6, text="")
prevSong3show_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong4date_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong4time_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong4title_lbl    = ttk.Label(tickFrame, padding=6, text="")
prevSong4artist_lbl   = ttk.Label(tickFrame, padding=6, text="")
prevSong4composer_lbl = ttk.Label(tickFrame, padding=6, text="")
prevSong4show_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong5date_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong5time_lbl     = ttk.Label(tickFrame, padding=6, text="")
prevSong5title_lbl    = ttk.Label(tickFrame, padding=6, text="")
prevSong5artist_lbl   = ttk.Label(tickFrame, padding=6, text="")
prevSong5composer_lbl = ttk.Label(tickFrame, padding=6, text="")
prevSong5show_lbl     = ttk.Label(tickFrame, padding=6, text="")

#Place labels
songName_lbl.grid(    column=0, row=1, columnspan=3, sticky=W)
songArtist_lbl.grid(  column=0, row=2, columnspan=3, sticky=W)
songComposer_lbl.grid(column=0, row=3, columnspan=3, sticky=W)
psa_lbl.grid(         column=0, row=1, columnspan=3, sticky=W)

#Place Instructions
howTo_Show_lbl.grid(column=0, row=0, columnspan=5, sticky=W)
howTo_Song_lbl.grid(column=0, row=0, columnspan=5, sticky=W)
howTo_ID_lbl.grid(  column=0, row=0, columnspan=5, sticky=W)
howTo_PSA_lbl.grid( column=0, row=0, columnspan=5, sticky=W)

#Place ticker Labels
prevSong1date_lbl.grid(    column=0,  row=0, columnspan=2, sticky=(W, E))
prevSong1time_lbl.grid(    column=2,  row=0, columnspan=2, sticky=(W, E))
prevSong1title_lbl.grid(   column=4,  row=0, columnspan=2, sticky=(W, E))
prevSong1artist_lbl.grid(  column=6,  row=0, columnspan=2, sticky=(W, E))
prevSong1composer_lbl.grid(column=8,  row=0, columnspan=2, sticky=(W, E))
prevSong1show_lbl.grid(    column=10, row=0, columnspan=2, sticky=(W, E))

prevSong2date_lbl.grid(    column=0,  row=1, columnspan=2, sticky=(W, E))
prevSong2time_lbl.grid(    column=2,  row=1, columnspan=2, sticky=(W, E))
prevSong2title_lbl.grid(   column=4,  row=1, columnspan=2, sticky=(W, E))
prevSong2artist_lbl.grid(  column=6,  row=1, columnspan=2, sticky=(W, E))
prevSong2composer_lbl.grid(column=8,  row=1, columnspan=2, sticky=(W, E))
prevSong2show_lbl.grid(    column=10, row=1, columnspan=2, sticky=(W, E))

prevSong3date_lbl.grid(    column=0,  row=2, columnspan=2, sticky=(W, E))
prevSong3time_lbl.grid(    column=2,  row=2, columnspan=2, sticky=(W, E))
prevSong3title_lbl.grid(   column=4,  row=2, columnspan=2, sticky=(W, E))
prevSong3artist_lbl.grid(  column=6,  row=2, columnspan=2, sticky=(W, E))
prevSong3composer_lbl.grid(column=8,  row=2, columnspan=2, sticky=(W, E))
prevSong3show_lbl.grid(    column=10, row=2, columnspan=2, sticky=(W, E))

prevSong4date_lbl.grid(    column=0,  row=3, columnspan=2, sticky=(W, E))
prevSong4time_lbl.grid(    column=2,  row=3, columnspan=2, sticky=(W, E))
prevSong4title_lbl.grid(   column=4,  row=3, columnspan=2, sticky=(W, E))
prevSong4artist_lbl.grid(  column=6,  row=3, columnspan=2, sticky=(W, E))
prevSong4composer_lbl.grid(column=8,  row=3, columnspan=2, sticky=(W, E))
prevSong4show_lbl.grid(    column=10, row=3, columnspan=2, sticky=(W, E))

prevSong5date_lbl.grid(    column=0,  row=4, columnspan=2, sticky=(W, E))
prevSong5time_lbl.grid(    column=2,  row=4, columnspan=2, sticky=(W, E))
prevSong5title_lbl.grid(   column=4,  row=4, columnspan=2, sticky=(W, E))
prevSong5artist_lbl.grid(  column=6,  row=4, columnspan=2, sticky=(W, E))
prevSong5composer_lbl.grid(column=8,  row=4, columnspan=2, sticky=(W, E))
prevSong5show_lbl.grid(    column=10, row=4, columnspan=2, sticky=(W, E))


root.mainloop()
