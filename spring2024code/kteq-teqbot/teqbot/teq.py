"""KTEQ-FM TEQBOT CLASS.

This module contains the TeqBot class, the main component of the kteq-teqbot
project. Several methods in this class serve as wrappers for API calls and
other scripts in this repository. This abstraction was implemented so that
all of the complicated logic could be separated from this module,
allowing most of the TeqBot module to handle scheduling tasks.

Example:

        $ python teqbot.py

Ordinarily, the teqbot.py module will not be run via command line. Instead,
the module will be loaded in, allowing for an instance of the TeqBot class
to be created. This class can run a scheduler for performing various tasks
related to a provided IceCast music station. Current tasks involve updating
metadata from a music stream to slack and TuneIn, as well as sending stream
status updates to slack with diagnosis messages when the stream is not
operating properly.

Attributes:
    STANDARD_FREQUENCY (int): default frequency in seconds for scheduler
    NOW_PLAYING (str): bitstring corresponding to now playing task
    STREAM_STATUS (str): bitstring corresponding to stream status task
    CHECK_LYRICS (str): bitstring corresponding to check lyrics task
    SWEAR_LOG (str): bitstring corresponding to swear log task
    OPTION_5 (str): bitstring corresponding to placeholder task 5
    OPTION_6 (str): bitstring corresponding to placeholder task 6
    OPTION_7 (str): bitstring corresponding to placeholder task 7
    OPTION_8 (str): bitstring corresponding to placeholder task 8
    ROBOT_EMOJI (str): robot face emoji
    SKULL_EMOJI (str): skull emoji
    MUSIC_EMOJI (str): musical note emoji

Todo:
    * Create the update task for automatically updating scheduler
    * Create other additional tasks as they are needed

.. _TeqBot GitHub Repository:
   https://github.com/kteq-fm/kteq-teqbot

.. _KTEQ-FM Website:
   http://www.kteq.org/

"""

from slackclient import SlackClient
import os
import time
import slack
import stream
import tunein
import genius
import log
import shlex
import subprocess

#standard frequency (in seconds)
STANDARD_FREQUENCY = 5

NOW_PLAYING   = '00000001'
STREAM_STATUS = '00000010'
CHECK_LYRICS  = '00000100'
SWEAR_LOG     = '00001000'
OPTION_5      = '00010000'
OPTION_6      = '00100000'
OPTION_7      = '01000000'
UPDATE_REPO   = '10000000'

#feel free to add more emojis to this list
ROBOT_EMOJI = ':robot_face:'
SKULL_EMOJI = ':skull:'
MUSIC_EMOJI = ':musical_note:'

class TeqBot:
    """TeqBot, the class for handling stream monitoring tasks

    The TeqBot class is the main component of this project, and essentially
    handles operations of all other modules in this repository through
    wrapper methods.

    Attributes:
        slack (slackclient._client.SlackClient):
            slackclient object used to perform slack API calls
        stream (str): URL of IceCast Stream
        python (str): Path to Python3 executable for task spawning
        tuneInStationID (str): TuneIn Station ID value
        tuneinPartnerID (str): TuneIn Partner ID
        tuneinPartnerKey (str): TuneIn Partner Key
        username (str): Username of TeqBot as it appears in slack
        emoji (str): Emoji that represents TeqBot's slack user icon
        channel (str): Current Channel ID TeqBot is pointing to for posting
        message (str): Current prepared message for TeqBot to sent on slack
        lastSong (str): Last song played on IceCast stream

    """

    def __init__(self):
        """TeqBot class initialization method.

        The TeqBot __init__ method's most important task is to read in
        several environment variables in order for the bot to function.
        These variables are stored as environmental variables in order
        to maintain a level of confidentiality, as some of these values
        should not be widely distributed. These environmental variables
        can be modified to simple hardcoded information, but this is
        generally not recommended.

        Default values are also assigned to TeqBot's slack properties.
        The default name for TeqBot on slack is 'TEQ-BOT', and the
        default emoji is the robot face.

        """
        self.slack  = SlackClient( os.environ.get('SLACK_TOKEN') )
        self.stream = os.environ.get('STREAM_URL')
        self.python = os.environ.get('PYTHONPATH')
        self.tuneinStationID  = os.environ.get('TUNEIN_STATION_ID')
        self.tuneinPartnerID  = os.environ.get('TUNEIN_PARTNER_ID')
        self.tuneinPartnerKey = os.environ.get('TUNEIN_PARTNER_KEY')
        self.geniusToken = { 'Authorization' : 'Bearer ' + os.environ.get('GENIUS_TOKEN') }
        self.logger = os.environ.get('LOGGERPATH')
        self.username = 'TEQ-BOT'
        self.emoji    = ROBOT_EMOJI
        self.channel = None
        self.message = ""
        self.lastSong = ""
        self.lastSwear = None

    def scheduler(self, event='11111111', frequency=STANDARD_FREQUENCY):
        """Scheduler for spawning TeqBot tasks at predetermined intervals.

        This method will first determine which tasks will be called by
        performing bitwise operations. Each task is assigned to a bit
        in an 8-bit string; if the given task's bit is set to 1, that
        task will be spawned when the scheduler triggers events.

        The scheduler then goes into a potentially infinite loop. Each
        task has a 'clock' that monitors how many seconds have elapsed
        since the task was last spawned. Once a clock has hit the value
        equivalent to the task's frequency, the task will be executed.
        These tasks are spawned as new processes, which helps prevent
        the entire scheduler from crashing if one particular process
        encounters a runtime error for whatever reason.

        After updating the clock on each cycle, the scheduler checks on
        TeqBot's stat file. If this stat file reads 'Done', the scheduler
        will terminate operations. This offers TeqBot a graceful way to
        cease operations without killing the scheduler's process. The stat
        file can be updated using the TeqBot.set_stat_file() method. Ending
        the scheduler will delete the TeqBot stat file.

        Args:
            event (str): events string. Later converted to binary for bitwise
                operations for determining which tasks are called. Defaults
                to '11111111', which dictates that all tasks should be spawned.
            frequency (int): The base frequency for when tasks are spawned.
                This value is in seconds, so a frequency of value 60 means
                the base frequency for the tasks is once every minute.
                Defaults to STANDARD_FREQUENCY, a value at the top of
                teq.py that can be modified. This value should be 60 normally.

        """
        # reset some flags
        nowPlayingClock   = 0
        streamStatusClock = 0
        updateRepoClock   = 0
        checkLyricsClock  = 0
        swearLogClock     = 0

        self.set_last_played("None")
        self.set_stat_file("Running")
        self.get_last_played()

        # determine which tasks will be called
        nowPlaying   = int( "{0:b}".format( int( event, 2) & int(NOW_PLAYING,   2) ) )
        streamStatus = int( "{0:b}".format( int( event, 2) & int(STREAM_STATUS, 2) ) )
        updateRepo   = int( "{0:b}".format( int( event, 2) & int(UPDATE_REPO,   2) ) )

        # New tasks in dev
        checkLyrics   = int( "{0:b}".format( int( event, 2) & int(CHECK_LYRICS, 2) ) )
        swearLog      = int( "{0:b}".format( int( event, 2) & int(SWEAR_LOG,    2) ) )

        print("running Scheduler")
        while True:
            #trigger events
            if nowPlaying and nowPlayingClock % (frequency * 2) == 0:
                # only check nowplaying at 1/2 frequeny
                print("Handling NowPlaying Status...")
                self.spawn_task(self.python + " teqbot task --nowplaying")
                nowPlayingClock = 1
            if streamStatus and streamStatusClock % (frequency * 20) == 0:
                # only check status at 1/20th frequency
                print("Handling Stream Status...")
                self.spawn_task(self.python + " teqbot task --status")
                streamStatusClock = 1
            if checkLyrics and checkLyricsClock % frequency == 0:
                # update repo at normal frequency
                print("Checking Lyrics...")
                self.spawn_task(self.python + " teqbot task --lyric")
                checkLyricsClock = 1
            if swearLog and swearLogClock % frequency == 0:
                # update repo at normal frequency
                print("Checking Swear Log...")
                self.spawn_task(self.python + " teqbot task --swear")
                swearLogClock = 1
            if updateRepo and updateRepoClock % (frequency * 1200) == 0:
                # update repo at 1/1200th frequency
                print("Updating TeqBot...")
                self.spawn_task(self.python + " teqbot task --update")
                updateRepoClock = 1
            time.sleep(1)
            nowPlayingClock   += 1
            streamStatusClock += 1
            updateRepoClock   += 1
            checkLyricsClock  += 1
            swearLogClock     += 1
            print("n:", nowPlayingClock,
                  "s:", streamStatusClock,
                  "l:", checkLyricsClock,
                  "w:", swearLogClock,
                  "u:", updateRepoClock)

            # break out of the scheduler if stat file contains "Done"
            if self.check_stat_file("Done"):
                self.delete_stat_file()
                break

        # end of loop
        print("Finished Scheduler")

    def spawn_task(self, command):
        """Spawn a task as a new process.

        Simply splits a command into individual command line
        arguments, then spawns a new task using subprocess.Popen().
        This will be updated in the future if there ever arises
        any TeqBot tasks that require the use of redirecting
        output, but as of right now each individual task is
        self-contained and does not really pass on any new
        information to other tasks.

        Args:
            command (str): terminal command for new task.

        """
        # split args into separate entries in a list
        args = shlex.split(command)
        # spawn new process
        p    = subprocess.Popen(args)

    def task_now_playing(self):
        """Update the current song's information to slack and TuneIn.

        Using the TeqBot.get_last_played() method to read the
        text file that stores the last song played, TeqBot checks the
        current live song being played to determine if a new song
        is playing. If a new song is playing, TeqBot will update
        the #nowplaying channel with the song information. TeqBot
        will also update the TuneIn metadata, allowing listeners
        using the TuneIn program to view song information, as well
        as album art for the current song!

        Note:
            if TeqBot is shut down during a song, and then rebooted
            before the song is finished, it is possible (and likely)
            that TeqBot will post the same song twice.
            In order for TeqBot to successfully post to slack,
            create a "#nowplaying" channel. Make sure to mute it,
            as this channel will be updated very often.

        """
        self.get_last_played()
        # compare last song to what is currently playing
        print("NOW PLAYING: Comparing", self.lastSong, "|", self.get_now_playing() )
        newsong = self.check_last_played()
        if newsong:
            print("New Song")
            # update #nowplaying on slack
            self.teq_message(self.now_playing(self.lastSong), "nowplaying", MUSIC_EMOJI)
            # post metadata to TuneIn
            self.tunein(self.lastSong)
        else:
            print("Same Song")

    def task_stream_status(self):
        """Check if the stream is online

        The stream is checked using the TeqBot.ping_stream()
        wrapper method for the stream.ping_stream() method.

        If the stream is online, TeqBot will output a message
        indicating such (this is only on terminal, no actual
        posts are made when the stream is normal.)

        If the stream is offline, TeqBot will use the message
        returned by TeqBot.ping_stream() to diagnose the problem.
        TeqBot will then notify the #engineering channel that
        the stream is down, as well as provide the error message.
        TeqBot will inform the #engineering channel that the stream
        is still down every time the event is triggered until the
        stream is restored to an online status.

        Note:
            TeqBot.task_stream_status() happens at (1/5) frequency.
            For example, if frequency is set to 60 (seconds),
            the stream status will only be checked once every
            five minutes.
            In order for TeqBot to successfully post to slack,
            create an "#engineering" channel. Make sure this channel
            has notifications on often, depending on how urgent
            it is for your stream to be online constantly.

        """
        for i in range(0, 5):
            online, msg = self.ping_stream()
            # make 5 attempts to connect.
            if online:
                break
        if online:
            # Only do something if the stream HAD been down
            # If this is the case, then let everyone know
            # We are back online
            if self.check_stat_file("Stream Down"):
                self.set_stat_file("Running")
                msg = "The Stream is Back Online!"
                print(msg)
                self.teq_message(msg, "engineering", ROBOT_EMOJI )
            else:
                print("Stream is Online")
        else:
            # stream is down, let everyone know
            print(msg)
            self.teq_message(msg, "engineering", SKULL_EMOJI )
            self.set_stat_file("Stream Down")

    def task_check_lyrics(self):
        """Perform a quick auto-check of a song's lyrics

        This tasks reads a nowPlaying.txt file to determine
        what song is currently being played on KTEQ. After
        determining the song, this task will attempt to
        locate song lyrics if they haven't yet been found.
        After finding the lyrics, a preliminary search for
        swear words will be conducted, and a report will be
        sent to a lyrics.txt file which can be read in by another
        program.

        This task uses a nowPlaying text file to determine
        the current song playing and is independed of the
        nowplaying task. This allows this function to still
        operate even in the event that the stream is down.

        This task incorporates functionality with the kteq-song-logger
        program found at https://github.com/KTEQ-FM/kteq-song-log.
        """
        np   = self.get_now_playing_logger()
        last = self.get_last_lyric()

        print("LYRIC: Comparing", np, "|", last )
        if np != last:
            self.set_last_lyric(np)
            song, artist = self.split_metadata(np)
            bad_words = self.get_profanity()
            msg = ""

            # Perform genius search and compose message(s)
            msg, clean = genius.run(song,artist,bad_words,self.geniusToken)

            if not clean:
                # If current song isn't clean, post to slack
                warning_msg = ""
                warning_msg += "Warning! Song Currently Playing On KTEQ "
                warning_msg += "may contain swears. Generating Report...\n"
                warning_msg += "```" + msg + "```"
                self.teq_message(warning_msg, "engineering", SKULL_EMOJI)

            # Post to lyrics.txt file
            self.post_lyrics(msg)
        else:
            print("Same Lyrics")

            #print(msg)






    def task_swear_log(self):
        """Submit swear log entries to slack

        This tasks reads a json file containing data for a
        swear log and passes this information to a slack
        channel.

        If a new swear log entry has been submitted recently, this
        will be sent to slack so that management can be informed of the
        event.

        This task incorporates functionality with the kteq-song-logger
        program found at https://github.com/KTEQ-FM/kteq-song-log.
        """


        # Read json file
        filename = "swear.json"
        filename = os.path.join(self.logger, filename)

        data = log.read_json(filename)

        filename = "lastSwear.json"
        filename = os.path.join(self.logger, filename)
        lastSwear = log.read_json(filename)

        print("LOG: Comparing\n", data, "|\n", lastSwear )
        if not log.compare_json(data, lastSwear):
            # Not Identical, New json file
            log.write_json(data,filename)

            swear_msg = log.generate_swear_log(data)

            # If message contains anything, submit
            if swear_msg:
                self.teq_message(swear_msg, "engineering", SKULL_EMOJI)
            print("New Log Found")




    def task_update_repo(self):
        """Update TeqBot's repository (NOT IMPLEMENTED)

        This is a placeholder function for a task with the
        intention to be a method for updating TeqBot's repo
        with new updates without having to stop TeqBot from
        running.

        This is still a very far out feature. Sorry.

        Notes:
            * Create a new branch just for teqbot updates
            * As of right now, if this were implemented,
                the update task would handle updates
                related to the stream status task and
                the now playing task, but would not
                handle any changes to the teq module,
                including any bug fixes or updates to
                the scheduler itself. Keep this in mind.

        """

        # temporary solution...
        self.spawn_task("/usr/bin/git pull")

    def teq_message(self, message, channel, emoji):
        """Create a message, set post emoji, then post message to slack.

        A bundled method for sending a new TeqBot message
        to a particular channel.
        An emoji can be supplied in order to give an
        icon somehow related to the content of the message.
        For instance, the #nowplaying updates can use
        a musical not emoji, whereas an emergency post
        can have a skull icon to implicate urgency. The
        emoji for TeqBot is reset to the robot face
        emoji after each message post.

        Args:
            message (str): message to be sent.
            channel (str): slack channel for the message.
            emoji   (str): emoji for the message.

        """
        'set emoji and prepare a message, send'
        self.set_emoji(emoji)
        self.set_message(message)
        self.set_channel(channel)
        status, msg = self.send_message()
        # reset the emoji to the standard robot face
        self.set_emoji(ROBOT_EMOJI)
        if status:
            print("Sent Message:", msg )
        else:
            print("Error: ", msg )

    def set_emoji(self, emojiName):
        """Set the emoji used to represent TeqBot on slack.

        A simple setter function for assigning an emoji
        to TeqBot. Emojis are used in slack posts as TeqBot's
        user icon.

        Args:
            emojiName (str): name of the emoji used for TeqBot.
            channel (str): slack channel for the message.
            emoji   (str): emoji for the message.

        Note:
            please view http://www.webpagefx.com/tools/emoji-cheat-sheet/
            for examples of valid emoji parameters.

        """
        self.emoji = emojiName

    def set_channel(self, channel):
        """Set the channel TeqBot will be posting on.

        A simple setter function for assigning a channel
        for TeqBot to post on.

        Args:
            channel (str): name of the channel TeqBot will post to.

        Note:
            The value set in TeqBot.channel is the channel's ID.

        """
        'set the channel id for TeqBot'
        self.channel = slack.get_channel_id(self.slack, channel)

    def set_last_song(self, song):
        """Set the last song played on the stream.

        A simple setter function for assigning a song as the
        last song played on whatever stream TeqBot is monitoring

        Args:
            song (str): The song being assigned to the lastSong.

        """
        self.lastSong = song

    def set_message(self, message):
        """Set the message TeqBot will be posting

        A simple setter function for assigning a message for
        TeqBot to post to slack.

        Args:
            message (str): TeqBot message to be sent soon.

        Note:
            This method does not actually post the message.
            Message posting to slack is done via the
            TeqBot.send_message() command.
            The TeqBot.teq_message() method is a wrapper
            for handling all properties that need to be
            set before properly posting a message to slack.

        """
        self.message = message

    def get_channels(self):
        """Get a list of channels on slack

        A wrapper for the slack.get_channels() command for
        gathering all existing channels for a given slack
        team.

        Returns:
            list: List of public slack channels.

        Note:
            This does not list private channels.

        """
        'get the list of channels'
        return slack.get_channels(self.slack)

    def get_channel_info(self):
        """Get a particular channel's info

        A wrapper for the slack.get_channel_info() command for
        returning information about a particular slack
        channel.

        Returns:
            str: Information about the current slack channel.

        """
        return slack.get_channel_info(self.slack, self.channel)

    def get_now_playing(self):
        """Get the current song being played

        A wrapper for the stream.ping_stream() command for
        returning information about the current song being
        played on an IceCast stream server.

        Returns:
            str: Current song metadata retrieved from IceCast.
        Note:
            This function relies on IceCast's metadata being
            updated on at least a mostly regular basis.

        """
        ping, message = stream.ping_stream(self.stream)
        return message

    def get_profanity(self, filename="profanity.txt"):
        """Get Profanity List.

        This function opens a profanity.txt file to load in a list of bad
        words. oh my!

        Returns:
            str: List of bad words :(
        Note:
            This function relies on a "profanity.txt" file to be present
            in the directory set with the LOGGERPATH environment variable.
            a different filename can be provided if needed.
        """
        filename = os.path.join(self.logger, filename)
        return genius.load_profanity(filename)

    def get_now_playing_logger(self, filename="nowPlaying.txt"):
        """Get the current song being played based on a nowplaying.txt file

        This differs from get_now_playing() in that this function
        attempts to get now playing information from a text file rather than
        an IceCast stream server, allowing for this to work offline as long
        as a nowplaying file exists.

        Returns:
            str: Current song metadata retrieved from text file.
        Note:
            This function relies on a "nowPlaying.txt" file to be present
            in the directory set with the LOGGERPATH environment variable.
            a different filename can be provided if needed.
        """
        filename = os.path.join(self.logger, filename)
        with open(filename, 'r', newline='') as np:
            return "".join(np.readlines())

    def post_lyrics(self,lyrics,filename="lyrics.txt"):
        """Post Lyrics to a lyrics.txt file

        This differs from get_now_playing() in that this function
        attempts to get now playing information from a text file rather than
        an IceCast stream server, allowing for this to work offline as long
        as a nowplaying file exists.

        Returns:
            None

        Note:
            This function writes a "lyrics.txt" file to the directory set
            with the LOGGERPATH environment variable.
            a different filename can be provided if needed.
        """
        filename = os.path.join(self.logger, filename)
        with open(filename, 'w') as ly:
            ly.write(lyrics)


    def ping_stream(self):
        """Check if the stream is online.

        A wrapper for the stream.ping_stream() command for
        returning information about whether the stream is
        currently up or not.

        Returns:
            (tuple): tuple containing:

                ping (bool): True if stream is up, False
                    if stream is down.
                message (str): error message for why stream is
                    down, if it is.

        """
        ping, message = stream.ping_stream(self.stream)
        return ping, message

    def compare_songs(self):
        """Compare current song with last played to see if this is a new song.

        This method compares the current song playing on IceCast with
        the song currently stored as TeqBot.lastSong. If the songs are
        identical, it can be determined the same song is playing since the
        last check. If The songs are not identical, a new song is being
        played. This new song is then set as the TeqBot.lastSong.

        Returns:
            bool: True if a new song is playing, False otherwise

        """
        check = self.get_now_playing()
        if self.lastSong != check:
            #new song
            self.set_last_song( check )
            return True
        else:
            #same song
            return False

    def print_channel_list(self):
        """Compare current song with last played to see if this is a new song.

        This method compares the current song playing on IceCast with
        the song currently stored as TeqBot.lastSong. If the songs are
        identical, it can be determined the same song is playing since the
        last check. If The songs are not identical, a new song is being
        played. This new song is then set as the TeqBot.lastSong.

        Returns:
            bool: True if a new song is playing, False otherwise

        """
        channels = self.get_channels()
        if channels:
            print("KTEQ-MGMT Channel List:")
            for channel in channels:
                print("    #" + channel['name'] + " (" + channel['id'] + ")")

    def send_message(self):
        """Send a predetermined message to TeqBot's current channel

        A wrapper for the slack.send_message() command for sending
        a message to a slack channel. After performing this method,
        the TeqBot.message field is cleared out to avoid duplicate
        posts.

        Note:
            The TeqBot.teq_message() method is a more concise way to
            generate and post messages to slack. The TeqBot.teq_message()
            method contains parameters for modifying the channel, the message,
            and the emoji used for the post. This allows for that method to
            be called, rather than consecutive setter methods, then this one.

        """
        status, msg = slack.send_message(self.slack, self.channel, self.message, self.username, self.emoji)
        #clear the message afterwards
        self.set_message("")
        return status, msg


    def set_last_played(self, song):
        """Store the metadata for the last song in a teq file

        This method stores the metadata from a song in a hidden
        .teq.song file in the directory which the teqbot program
        was executed.

        Args:
            song (str): Song metadata to be posted in file.

        """
        f = open('.teq.song', 'w')
        f.write(song)

    def get_last_played(self):
        """Read the teq song file to retrieve last song played.

        This method reads the metadata of a song from a hidden
        .teq.song file. This metadata is stored in the
        TeqBot.lastSong variable.

        """
        if os.path.exists('.teq.song'):
            f = open('.teq.song', 'r')
            self.lastSong = f.read()
        else:
            self.lastSong = ""

    def set_last_lyric(self, song):
        """Store the metadata for the last song lyric in a teq file

        This method stores the metadata from a song in a hidden
        .teq.lyric file in the directory which the teqbot program
        was executed.

        Similar to the .teq.song file, but for updating lyrics.

        Args:
            song (str): Song metadata to be posted in file.

        """
        f = open('.teq.lyric', 'w')
        f.write(song)

    def get_last_lyric(self):
        """Read the teq song lyric to retrieve last song played.

        This method reads the metadata of a song from a hidden
        .teq.lyric file.

        """
        if os.path.exists('.teq.lyric'):
            f = open('.teq.lyric', 'r')
            return f.read()
        else:
            return ""

    def check_last_played(self):
        """Check the teq song file to determine if a new song is being played.

        If the .teq.song file is present, read the file to determine what song
        is being played. Next, get the current playing song from the IceCast
        server. If the songs are not the same, then a new song is being played.

        Returns:
            bool: True if new song being played, False otherwise

        """
        if os.path.exists('.teq.song'):
            f = open('.teq.song', 'r')
            check = self.get_now_playing()
            song = f.read()
            if song == "None":
                self.set_last_song( check )
                self.set_last_played( check )
                return True

            elif check != song:
                # New Song
                self.set_last_song( check )
                self.set_last_played( check )
                return True

            else:
                return False
        else:
            return False

    def set_stat_file(self, status):
        """Set the value of the teq status file

        This function writes a value to the hidden .teq.stat
        file. This status file is monitored by the scheduler.

        The stat file will display the following information:
            Running: schduler is running, stream is online.
            Stream Down: schduler is running, stream is offline.
            Done: scheduler is done, will close the next time
                stat file is polled.

        Args:
            status (str): Data to be written to .teq.stat file

        """
        f = open('.teq.stat', 'w')
        f.write(status)

    def check_stat_file(self, check):
        """Check to see if the status file is a current value.

        This function compares the message contained in the
        .teq.stat file with the check parameter. If the two
        values are identical, this function returns true. If
        not, the stat file is not the same as the check parameter.

        Args:
            check (str): Status being checked in the stat file.

        Returns:
            bool: True if status of stat file is identical to check
                variable, False otherwise or if stat file isn't present.
        """
        if os.path.exists('.teq.stat'):
            f = open('.teq.stat', 'r')
            stat = f.read()
            return check == stat
        else:
            return False

    def delete_stat_file(self):
        """Delete the status file.

        This function deletes the .teq.stat file. This occurs
        when the scheduler closes, as the status file should
        not be present when TeqBot is not running.

        Note:
            In rare instances where the .teq.stat file is
            present after the scheduler completes, the file
            should be manually removed.
        """
        if os.path.exists('.teq.stat'):
            os.remove('.teq.stat')

    def tunein(self, metadata):
        """Post Metadata to TuneIn After Formatting.

        A wrapper for the tunein.post() command for sending
        song metadata to TuneIn. This metadata is formatted
        in the tunein.post() function to fit TuneIn's API
        calls for updating metadata on a livestream. This
        allows for the artist and song name to be individually
        recognized by TuneIn when playing a particular song,
        allowing for album art to be displayed to listeners
        when streaming a station on TuneIn, both the mobile
        app and the Web application.

        Note:
            There are a few issues in how tunein.post()
            is currently working, which are detailed in the
            tunein module of this project.
        """
        tunein.post( self.tuneinStationID, self.tuneinPartnerID, self.tuneinPartnerKey, metadata)

    def now_playing(self, metadata):
        """Clean Metadata for posting to slack.

        Note:
            The reason for the formatting is so that tunein
            can distinguish where the split between artist
            and song are in the metadata. Other streams
            don't seem to particularly care about this
            distinction.
        """
        return metadata.replace("__by__", "by")

    def split_metadata(self, metadata):
        """Clean metadata into song and artist tuple

        """
        # split the metadata at the correct position
        split  = metadata.split("__by__", 1)
        song   = split[0].rstrip().lstrip()

        # check if artist and song were split
        if len(split) > 1:
            artist = split[1].rstrip().lstrip()
        else:
            artist = ""

        return song,artist

if __name__ == "__main__":
    teq = TeqBot()

    print("Hello! My name is", teq.username, "\n")
    if os.environ.get('SLACK_TOKEN'):
        print("Slack Token properly loaded")
    else:
        print("Slack Token not loaded!!")
    if teq.stream:
        print("Stream URL properly loaded")
    else:
        print("Stream URL not loaded!!")
    if teq.python:
        print("Python Path properly loaded")
    else:
        print("Python Path not loaded!!")
    if teq.tuneinStationID:
        print("TuneIn Station ID properly loaded")
    else:
        print("TuneIn Station ID not loaded!!")
    if teq.tuneinPartnerID:
        print("TuneIn Partner ID properly loaded")
    else:
        print("TuneIn Partner ID not loaded!!")
    if teq.tuneinPartnerKey:
        print("TuneIn Partner Key properly loaded")
    else:
        print("TuneIn Partner Key not loaded!!")

    print("\nIt's nice to meet you!!")
