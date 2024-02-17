"""KTEQ-FM STREAM STATUS FUNCTIONS.

This module contains the functions for retrieving stream status from an 
IceCast music broadcast server. These functions are performed by making 
HTTP requests to the IceCast server, then analyzing the html retrieved from 
the site to determine stream status, and report what song is currently being 
played on the station.

Example:

        $ python stream.py "<YOUR_STREAM_URL>"

Running this module from command line, if provided with a valid IceCast stream
url, will report whether the stream is currently online or not. If the stream 
is online, the current song will also be reported.

Attributes:
    NO_DATA (str): Error Code. No data retrieved from IceCast Server.
    URL_ERROR (str): Error Code. HTTP timeout, or bad internet connection.
    TIMEOUT_VALUE(int): Amount of time in seconds HTTP request will wait 
        before returning a urllib.error.URLError.

Todo:
    * Look into why false negatives are returned for stream status.

.. _TeqBot GitHub Repository:
   https://github.com/kteq-fm/kteq-teqbot

.. _KTEQ-FM Website:
   http://www.kteq.org/

"""

import sys
from urllib.request import urlopen
import urllib.error
from bs4 import BeautifulSoup

#potential stream errors
NO_DATA   = "no data read from Icecast Server"
URL_ERROR = "HTTP Request Timeout"

#how long to wait for timeout
TIMEOUT_VALUE = 60

def prep_message(cause="None"):
    """Prepare an error message to diagnose stream.

    Prepare a message to be generated and sent to the 
    slack channel designated for reporting stream incidents.
    The current incidents teq-bot can report on are:

    NO_DATA:   Icecast server is up, but no data is being output
               to it. This usually means that the stream is
               up, but Altacast encoders are not connected.
    URL_ERROR: Icecast is either down, or HTTP request simply
               simply timed out. Technically this happens
               purely because the HTTP request times out. 
               This can occur accidentally if internet speeds 
               happen to be slow at the time. However, 
               they can also mean that the timeout occurs 
               because the Icecast page isn't up at all.

    Args:
        cause (str): the error that explains how the stream is down

    Returns:
        msg (str): Error message based on cause of stream failure.

    Example:

        >>> import stream
        >>> msg = stream.prep_message(stream.NO_DATA)
        >>> msg
        <Prints stream error message for NO_DATA case>

    Warning: 
        Failing to supply cause param returns unknown error.
    
    Todo: 
        Add any additional error types encountered.
    """
    msg = "ALERT!! STREAM IS DOWN!!\n"
    msg = msg + "Likely cause: \n"
    if cause == NO_DATA:
        msg = msg + "No data read from Icecast server. \n"
        msg = msg + "This at least means the computer is on, "
        msg = msg + "and icecast is running, but the altacast "
        msg = msg + "encoders aren't hooked up properly. This "
        msg = msg + "most often happens when someone boots up "
        msg = msg + "multiple instances of altacast on the station "
        msg = msg + "computer. I would start with looking at that."
    elif cause == URL_ERROR:
        msg = msg + "HTTP Request Timeout. \n"
        msg = msg + "This could mean a multitude of things. "
        msg = msg + "Right off the bat, we know that icecast is "
        msg = msg + "acting off. This could be from the following "
        msg = msg + "problems: \n"
        msg = msg + "1) icecast has been closed on the computer\n"        
        msg = msg + "2) multiple instances of icecast are running\n"
        msg = msg + "3) the station computer has lost internet access\n"
        msg = msg + "4) the station computer is rebooting\n"
        msg = msg + "5) the station computer is off, either from "
        msg = msg + "shutting down or from crashing.\n\n"
        msg = msg + "When diagnosing this issue, please check on AltaCast "
        msg = msg + "as well, because that could also possibly be down.\n"
    else:
        msg = msg + "Unknown Error!!! \n"
        msg = msg + "This should have never happened. "
        msg = msg + "I have no idea what is wrong. I'm truly sorry.\n"
        msg = msg + "Just sit things out for a bit and and everything will "
        msg = msg + "be fine before long.\n"
    return msg

def now_playing(data):
    """Clean up streamdata html to return song information.

    Clean up a portion of HTML that contains the data for
    whatever song is currently broadcasting on an IceCast 
    stream.

    Once the song is identified in the message, a #NowPlaying 
    tag is added to it to identify the returned data as a 
    successful song ID.

    Full HTML example for KTEQ.ORG stream:
        [<td class="streamdata">KTEQ-FM</td>, 
        <td class="streamdata">91.3FM</td>, 
        <td class="streamdata">audio/mpeg</td>, 
        <td class="streamdata">
            Sun, 02 Oct 2016 13:33:52 Mountain Daylight Time
        </td>, 
        <td class="streamdata">192</td>, 
        <td class="streamdata">1</td>, 
        <td class="streamdata">6</td>, 
        <td class="streamdata">Alternative</td>, 
        <td class="streamdata">
            <a href="http://www.kteq.org/" target="_blank">http://www.kteq.org/</a>
        </td>, 
        <td class="streamdata">Beat Market by Sun Machine</td>, 
        <td class="streamdata">KTEQ-FM</td>, 
        <td class="streamdata">91.3FM</td>, 
        <td class="streamdata">audio/mpeg</td>, 
        <td class="streamdata">
            Sun, 02 Oct 2016 13:33:53 Mountain Daylight Time
        </td>, <td class="streamdata">96</td>, 
        <td class="streamdata">0</td>, 
        <td class="streamdata">4</td>, 
        <td class="streamdata">Alternative</td>, 
        <td class="streamdata">
            <a href="http://www.kteq.org/" target="_blank">http://www.kteq.org/</a>
        </td>, <td class="streamdata">Beat Market by Sun Machine</td>, 
        <td class="streamdata">KTEQ-FM</td>, 
        <td class="streamdata">91.3FM</td>, 
        <td class="streamdata">audio/mpeg</td>, 
        <td class="streamdata">
            Sun, 02 Oct 2016 13:33:54 Mountain Daylight Time
        </td>, 
        <td class="streamdata">128</td>, 
        <td class="streamdata">1</td>, 
        <td class="streamdata">6</td>, 
        <td class="streamdata">Alternative</td>, 
        <td class="streamdata">
            <a href="http://www.kteq.org/" target="_blank">http://www.kteq.org/</a>
        </td>, 
        <td class="streamdata">Beat Market by Sun Machine</td>]

    The crawler grabs this entire html segment, the only part needed is 
    the very last value in this list, which contains the song information.
    
    (In the case of KTEQ's Stream, there appear to be several duplicates.
    This is due to the fact that the kteq station has 3 encodings
    192kbps, 96kbps, 128kbps respectively. It is easiest to just
    grab the last encoding's song info, as they should all be the
    same and this method should work for any number of encodings
    on a given server.)

    Args:
        data (bs4.element.ResultSet): HTML segment containing song information 

    Returns:
        data (str): cleaned data string, containing just the song info.

    Example:

        >>> import stream
        >>> from urllib.request import urlopen
        >>> import urllib.error
        >>> from bs4 import BeautifulSoup
        >>> url  = <YOUR_STREAM_URL_HERE>
        >>> page = urlopen( url, timeout=60 )
        >>> soup = BeautifulSoup(page, 'html.parser')
        >>> data = soup.findAll('td', attrs={"class" : "streamdata" })
        >>> msg  = stream.now_playing(data)
        >>> msg
        '#NowPlaying Beat Market by Sun Machine'
    """
    # The very last <td> tagged value is the one we want. (contains song)
    data = str(data[-1])

    # get rid of html tags
    data = data.replace("<td class=\"streamdata\">","")
    data = data.replace("</td>","")

    # add '#NowPlaying: ' to the beginning of song information
    data = "#NowPlaying: " + data
    return data

def current_listeners(data):
    """Clean up streamdata html to return listener information.

    Parse through HTML to detemine listener count.

    Args:
        data (bs4.element.ResultSet): HTML segment containing 
            listener information 

    Returns:
        data (list): A pair of number in a list, corresponding to current 
            and peak listeners, respectively

    Example:

        >>> import stream
        >>> from urllib.request import urlopen
        >>> import urllib.error
        >>> from bs4 import BeautifulSoup
        >>> url  = <YOUR_STREAM_URL_HERE>
        >>> page = urlopen( url, timeout=60 )
        >>> soup = BeautifulSoup(page, 'html.parser')
        >>> data = soup.findAll('td')
        >>> msg  = stream.current_listeners(data)
        >>> msg
        [2, 16]
    """
    # The very last <td> tagged value is the one we want. (contains song)

    current = 0 # current listeners
    peak    = 0 # peak listeners

    for i in range(0, len(data)):
        if "Current Listeners:" in data[i].text:
            # next value corresponds to current listener count
            # for a particular encoding.
            current = current + int(data[i+1].text)
        elif "Peak Listeners:" in data[i].text:
            # next value corresponds to peak listener count
            # for a particular encoding.
            peak = peak + int(data[i+1].text)
    
    return [current, peak]

def ping_stream(url,listeners=False,debug=False):
    """Ping the music stream server for song info, stream status

    perform an HTTP request to copy all html data from an Icecast
    Stream. 

    If html data was successfullly retrieved:
        find all html tags labeled 'td' with attribute 'class=streamdata'
        if data was found:
            clean up the data to retrieve song information
            report that the stream is up, return song information
        if data was not found:
            report that the stream is down, return NO_DATA error message
    If HTTP request times out, resulting in no html data:
        report that the stream is down, return URL_ERROR error message

    This function uses the BeautifulSoup library for html parsing and
    urllib library to perform an HTTP request. After a successful HTTP request,
    the function parses the html retrieved from the stream's site. This 
    returns all of the html used for the site, which is pruned down to 
    instances of <td>, or table, tags in the site's html. In particular, this 
    pruning is done on <td> tags that have been labeled with the class "streamdata".
    While several of these cells contain other information about the stream, such 
    as bitrate, number of current listeners, station name, etc., the last cell 
    contains information about the currently playing song on the station as 
    long as icecast is pushing out metadata containing such information.

    If the http request fails to return any streamdata at all, this means that 
    while the Icecast page is up, there are no encoders being broadcasted.

    If the http request fails after the timeout threshold, this means that the 
    Icecast page is possibly down.

    Args:
        url (str): Online stream url.
        debug (bool): Optional flag for debugging outputs (unused)

    Returns:
            (tuple): tuple containing:

                bool: True if stream is up, False if stream is down.
                str: Song data if stream is up, Error message if stream is down

    Example:

        >>> import stream
        >>> url  = <YOUR_STREAM_URL_HERE>
        >>> msg = stream.ping_stream(url)
        >>> msg
        (True, '#NowPlaying: I Think I Smell a Rat by The White Stripes')
    """
    try:
        # Try to access the page for 60 seconds
        page = urlopen( url, timeout=TIMEOUT_VALUE )
        soup = BeautifulSoup(page, 'html.parser')

        # Check to see if "streamdata" exists
        data = soup.findAll('td', attrs={"class" : "streamdata" })

        # Also get counts
        count = soup.findAll('td')

        if listeners and len(count) > 0:
            # Stream is up, let's retrieve listener count
            return True, current_listeners(count)
        if len(data) > 0:
            # Stream is up, and retrieved current song data
            return True, now_playing(data)
        else:
            # IceCast Server is up, Altacast isn't.
            return False, prep_message(NO_DATA)
    except urllib.error.URLError:
        # http request timed out after 60 seconds
        # IceCast Server not set up, Altacast might also be down.
        return False, prep_message(URL_ERROR)

def usage():
    """Print Usage Statement.

    Print the usage statement for running stream.py standalone.

    Returns:
        msg (str): Usage Statement.

    Example:

        >>> import stream
        >>> msg = stream.usage()
        >>> msg
        'stream.py usage:\n$ python stream.py "<YOUR_STREAM_URL>"'
    """
    msg = "stream.py usage:\n"
    msg = msg + "$ python stream.py \"<YOUR_STREAM_URL>\""
    return msg
    

if __name__ == "__main__":
    if(len(sys.argv) > 1):
        ping, message = ping_stream(sys.argv[1], False, True)
        ping, counts = ping_stream(sys.argv[1], True, True)
        if ping:
            print("Station is online")
        else:
            print("Station is offline")
        print(message)
        print("Current Listeners:", counts[0])
        print("Peak    Listeners:", counts[1])
    else:
        print(usage())