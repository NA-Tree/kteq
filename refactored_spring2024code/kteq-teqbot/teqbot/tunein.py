"""KTEQ-FM TUNEIN API FUNCTIONS.

This module contains all of the TuneIn AIR API calls for the TeqBot project.
These api calls are all located centrally within this module for convenience.
All API calls will be built in this module, and corresponding wapper functions
will be created for each of these calls for TeqBot to use. The TuneIn AIR API
is used to update the song metadata on the TuneIn streaming application. This
allows for listeners to get real-time updates on songs being broadcast from the
online stream, with accompanying album art if available.

Please visit http://tunein.com/broadcasters/api/ for more information on how the
TuneIn AIR API works.

Example:

        $ python tunein.py "<TUNEIN_STATION_ID>" "<PARTNER_ID>" "<PARTNER_KEY>" "song" "artist"

Running this module from command line, if provided with a valid TuneIn AIR
API information, a song name, and an artist name, will post an update to
the TuneIn broadcast with the corresponding song and artist info.

Todo:
    * Fix how parseMetadata() works.

.. _TeqBot GitHub Repository:
   https://github.com/kteq-fm/kteq-teqbot

.. _KTEQ-FM Website:
   http://www.kteq.org/

"""

import requests
import sys
import urllib.parse

def post(sID, pID, pKey, metadata):
    """Post song information to TuneIn.

    Perform an HTTP GET request to post song name and artist name for a
    song to TuneIn. This will update this information to all listeners
    using TuneIn to stream.

    While a given TuneIn station ID can be easily discovered in the
    station's TuneIn URL, the TuneIn partner ID and partner key must
    be obtained by contacting TuneIn. Information regarding how to do
    this can be found at http://tunein.com/broadcasters/api/.

    Args:
        sID (str): TuneIn Station ID
        pID (str): TuneIn Partner ID
        pKey (str): TuneIn Partner Key
        metadata (str): Song metadata string containing
            song name and artist name.

    Example:

        >>> import tunein
        >>> metadata = "Square Peg Round Hole by WakeyWakey"
        >>> sID = "<TUNEIN_STATION_ID>"
        >>> pID = "<PARTNER_ID>"
        >>> pKey = "<PARTNER_KEY>"
        >>> tunein.post(sID, pID, pKey, metadata)

    Todo:
        Will need to devise a more sophisticated method of
        cleaning metadata in the future, as of right now
        this will screw up on any song with the actual word
        "by" in either the song name or the artist name.
        Easiest solution will be to set up the metadata
        so that the separator is something unique, that
        won't be entered on the DJ's end when recording
        songs on the station computer.
    """
    #split metadata into song and artist info
    song, artist = parseMetadata(metadata)

    #build the HTTP request
    msg = "http://air.radiotime.com/Playing.ashx?partnerId=" + pID
    msg = msg + "&partnerKey=" + pKey
    msg = msg + "&id=" + sID
    msg = msg + "&title="  + song
    if artist:
        msg = msg + "&artist=" + artist

    #prints the HTTP request to terminal, sends out as HTTP GET request
    print("Sending HTTP GET REQUEST:", msg)
    req = requests.get(msg)

def parseMetadata(metadata):
    """Convert metadata string into formatted song and artist strings.

    This function takes a full metadata string and splits it into an
    artist string and a song string. This allows TuneIn's application
    to distinguish the two fields for album art fetching. The function
    also modifies the strings so that they are ready for the tunein.post()
    function call, by replacing spaces with "+" symbols to work with
    the HTTP GET request.

    Args:
        metadata (str): Song metadata string containing
            song name and artist name.

    Returns:
            (tuple): tuple containing:

                song (str): Song Name.
                artist (str): Artist Name.

    Example:

        >>> import tunein
        >>> metadata = "Square Peg Round Hole by WakeyWakey"
        >>> msg = tunein.parseMetadata(metadata)
        >>> msg
        ('Square+Peg+Round+Hole', 'WakeyWakey')

    Todo:
        Will need to devise a more sophisticated method of
        cleaning metadata in the future, as of right now
        this will screw up on any song with the actual word
        "by" in either the song name or the artist name.
        Easiest solution will be to set up the metadata
        so that the separator is something unique, that
        won't be entered on the DJ's end when recording
        songs on the station computer.
    """

    # split the metadata at the correct position
    split  = metadata.split("__by__", 1)
    song   = split[0].rstrip().lstrip()

    # check if artist and song were split
    if len(split) > 1:
        artist = split[1].rstrip().lstrip()
    else:
        artist = None

    # get rid of NowPlaying tag, if present
    fullsong = song.split("#NowPlaying: ", 1)
    if len(fullsong) > 1:
        song = fullsong[1]
    else:
        song = fullsong[0]

    #clean up the song and artist strings
    song   = urllib.parse.quote_plus(song)
    artist = urllib.parse.quote_plus(artist)

    #return song and artist pair
    return song, artist

def usage():
    """Print Usage Statement.

    Print the usage statement for running tunein.py standalone.

    Returns:
        msg (str): Usage Statement.

    Example:

        >>> import tunein
        >>> msg = tunein.usage()
        >>> msg
        '<tunein.py usage statement>'
    """
    msg = "tunein.py usage:\n"
    msg = msg + "$ python tunein.py \"<TUNEIN_STATION_ID>\" "
    msg = msg + "\"<TUNEIN_PARTNER_ID>\" "
    msg = msg + "\"<TUNEIN_PARTNER_KEY>\" "
    msg = msg + "\"<SONG_NAME>\" "
    msg = msg + "\"<SONG_ARTIST>\" "
    return msg


if __name__ == "__main__":
    if(len(sys.argv) > 5):
        metadata =  sys.argv[4] + " __by__ " + sys.argv[5]
        post(sys.argv[1], sys.argv[2],  sys.argv[3], metadata)
    else:
        print(usage())
