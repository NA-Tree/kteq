import sys
from slackclient import SlackClient
import os
from teq import TeqBot

NOW_PLAYING   = '00000001'
STREAM_STATUS = '00000010'
CHECK_LYRICS  = '00000100'
SWEAR_LOG     = '00001000'
OPTION_5      = '00010000'
OPTION_6      = '00100000'
OPTION_7      = '01000000'
UPDATE_REPO   = '10000000'

def usage():
    usage = "\n\n"
    usage = usage + "===============\n"
    usage = usage + "KTEQ-FM TEQ-BOT\n"
    usage = usage + "===============\n\n"
    usage = usage + "=======================================\n"
    usage = usage + "By J. Anthony Brackins & Jonathan Dixon\n"
    usage = usage + "=======================================\n\n"
    usage = usage + "Requirements:\n"
    usage = usage + "Python3\n"
    usage = usage + "slackclient python library\n"
    usage = usage + "BeautifulSoup python library\n"
    usage = usage + "Slack API Token\n\n"
    usage = usage + "Usage:\n"
    usage = usage + "python3 teqbot <command> [options]\n\n"
    usage = usage + "Commands:\n\n"
    usage = usage + "\tusage             \t\tPrint Usage statement\n"
    usage = usage + "\tscheduler         \t\tRun the scheduler that handles calling each task\n"
    usage = usage + "\ttask              \t\tRun an individual scheduler task\n"

    usage = usage + "Scheduler Options:\n\n"
    usage = usage + "\t-n, --nowplaying  \t\tStart Up Nowplaying messages to slack\n"
    usage = usage + "\t-s, --status      \t\tCheck the status of the stream\n"
    usage = usage + "\t-l, --lyric       \t\tUpdate Lyrics being output to song logger\n"
    usage = usage + "\t-w, --swear       \t\tSend Swear Logs to slack\n"

    usage = usage + "Test Commands:\n\n"
    usage = usage + "\tkill          \t\tSend a message to stop the scheduler\n"
    usage = usage + "\tmessage <text>\t\tSend a test message to #boondoggling channel\n"

    return usage + "\n"

def command_handler(args):
    'check what command line argument was handled'
    args[0] = args[0].upper()
    #handle MESSAGE command:
    if "USAGE" in args:
        # Print Usage Statement
        print( usage() )
    elif "MESSAGE" in args:
        indx = args.index("MESSAGE")
        if len(args) > 1:
            # Send whatever message you enter as command line args
            msg = " ".join(args[indx+1:])
            print( "Sending \'" + msg + "\' to #boondoggling channel..." )
            #print( test_slack_message( msg ) )
    elif "SCHEDULER" in args:
        #reset stat file
        teq.delete_stat_file()

        # Set up all events to handle using BITWISE ops
        event = '00000000'

        if  "--nowplaying" in args or "-n" in args:
            event = "{0:b}".format( int( event, 2) | int(NOW_PLAYING, 2) )
        if "--status" in args or "-s" in args:
            event = "{0:b}".format( int( event, 2) | int(STREAM_STATUS, 2) )
        if "--lyric" in args or "-l" in args:
            event = "{0:b}".format( int( event, 2) | int(CHECK_LYRICS, 2) )
        if "--swear" in args or "-w" in args:
            event = "{0:b}".format( int( event, 2) | int(SWEAR_LOG, 2) )
        if "--update" in args or "-u" in args:
            event = "{0:b}".format( int( event, 2) | int(UPDATE_REPO, 2) )
        teq.scheduler(event)
    elif "TASK" in args:
        # ONLY run one individual task ONCE
        if  "--nowplaying" in args or "-n" in args:
            teq.task_now_playing()
        elif "--status" in args or "-s" in args:
            teq.task_stream_status()
        elif "--lyric" in args or "-l" in args:
            teq.task_check_lyrics()
        elif "--swear" in args or "-w" in args:
            teq.task_swear_log()
        elif "--update" in args or "-u" in args:
            teq.task_update_repo()
    elif "KILL" in args:
        print("Halting Scheduler running on different process...")
        teq.set_stat_file("Done")

#simply prints some channel info, then sends message to #boondoggling
def test_slack_message(message="Hello World!"):
    channels = teq.get_channels()
    if channels:
        for channel in channels:
            #send a message to boondoggling
            if channel['name'] == 'boondoggling':
                teq.set_channel(channel['name'])
                teq.set_message(message)
                teq.send_message()
                return "Message Sent."
    else:
        return "Unable to authenticate."

# get system arguments
teq = TeqBot()
args = sys.argv
if len(args) > 1:
    command_handler( args[1:] )
else:
    print( usage() )
