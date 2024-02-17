"""KTEQ-FM GENIUS API FUNCTIONS.

This module contains all of the Genius API calls for the TeqBot project.
These api calls are all located centrally within this module for convenience.
All API calls will be built in this module, and corresponding wapper functions
will be created for each of these calls for TeqBot to use. The Genius API
is used to look up song lyric information on the Genius lyrics website. This
allows for DJs to get an updated lyrics page for each song they log while
doing their set, as well as provide a preliminary search for profanity for
each song.

Please visit https://docs.genius.com/ for more information on how the
Genius API works.

Example:

        $ python genius.py "<SONG_NAME>" "<SONG_NAME>" "<GENIUS_TOKEN>(optional)"

Running this module from command line, if provided with a valid Genius
API information, a song name, and an artist name, will search for the queried
song on genius and return a report on the song lyrics

Todo:
    * Add additional tests

.. _TeqBot GitHub Repository:
   https://github.com/kteq-fm/kteq-teqbot

.. _KTEQ-FM Website:
   http://www.kteq.org/

"""

import sys
import requests
import os
from bs4 import BeautifulSoup
from nltk.stem.lancaster import LancasterStemmer
from difflib import SequenceMatcher

GENIUS_URL = "https://api.genius.com"

SONG_HAS_SWEARS = 0
SONG_SWEAR_FREE = 1
SONG_NOT_FOUND  = 2

def load_auth(token=None):
    """Convert Genius Token into required format.

    This function simply reformats a genius token if needed.

    Args:
        token (str): unformatted token

    Returns:
            (dict): Formatted token
    """
    if token is None:
        auth = 'Bearer ' + os.environ.get('GENIUS_TOKEN')
    else:
        auth = 'Bearer ' + token
    return { 'Authorization' : auth }

def similarity(a, b):
    """Calculate similarity between two strings.

    This function will compare two strings and determine how close they are
    to one another. This will allow for imprecise queries for song artists and
    song names, such as mispellings or other slight differences.

    Args:
        a (str): string being compared to b
        b (str): string being compared to a

    Returns:
            (double): similarity between a and b (1.0 indicates identical)

    Example:

        >>> import genius
        >>> genius.similarity("apples","oranges")
        0.46153846153846156
        >>> genius.similarity("apples","Appels")
        0.6666666666666666
        >>> genius.similarity("apples","apples")
        1.0
        >>> genius.similarity("Kendrick Lamar","Kendrick")
        0.7272727272727273
    """
    return SequenceMatcher(None, a, b).ratio()

def load_profanity(filename):
    """Load a profanity list from a file.

    creates a list to compare words to in order to determine profanity.
    A more robust profanity filter can be built by adding words to the file
    loaded, or by using different/multiple files.

    Args:
        filename (str): file containing swear words, one per line

    Returns:
            (list): list containing swear words
    """
    with open(filename) as f:
        return [ word.strip() for word in f.readlines() ]

def clean_test_01(lyrics, bad_words=None):
    """Check if lyrics are clean (TEST #1).

    given a string containing the song lyrics, determines if the song contains
    any profanity. This test uses the web API for http://wdylike.appspot.com/
    which gives a very simple boolean value of True if the song has profanity
    or False if the song is clean.

    Issues with this Test:
    This test is not very reliable for various reasons. This simply gives a
    yes or no response without returning a list of suspect words. Furthermore,
    the test uses very loosely defined regular expressions, allowing for several
    false positives. An example would be the query
    http://wdylike.appspot.com/?q=massive, which would return a True for
    explicit content because "massive" contains the word "ass" in it.

    Args:
        lyrics     (str): song lyrics
        bad_words (list): list of bad words (ignored for this test)

    Returns:
            (int): value indicating:
                    SONG_HAS_SWEARS if song has profanity.
                    SONG_SWEAR_FREE if song is clean.
                    SONG_NOT_FOUND  if failure to reach server.

            (list): empty list. Here to match structure of other
                    profanity tests, which actually
    """
    # URL is the true or false checker for profanity
    url = "http://www.wdylike.appspot.com"
    params = {'q': lyrics}

    # GET request, using the lyrics of song
    response = requests.get(url, params=params)

    test = None
    # Determine if song is clean, has swears, or other
    if 'true' in response.text :
        test =  SONG_HAS_SWEARS
    elif 'false' in response.text :
        test =  SONG_SWEAR_FREE
    else :
        test =  SONG_NOT_FOUND
    return [test, [] ]

def clean_test_02(lyrics, bad_words):
    """Check if lyrics are clean (TEST #2).

    given a string containing the song lyrics, determines if the song contains
    any profanity. This test uses a profanity list loaded in from a file to
    determine if songs are profane.

    Issues with this Test:
    This test will only catch words that have been added to a profanity file,
    so if a swear word is not present in this file, it will not be checked.
    Although this test uses lemmatization to reduce missed swears, this
    test will fail to find compound swear words, or swear words embedded into
    other words unless those compound words are added to the profanity file.
    An example would be the word "unf*ckable", which contains "f*ck" in the
    middle of it. This test does not use regular expressions so it might miss
    words like this. However, it would match the word "f*cking" as "f*ck" due
    to the lemmatizer.

    Args:
        lyrics     (str): song lyrics
        bad_words (list): list of bad words

    Returns:
            (int): value indicating:
                    SONG_HAS_SWEARS if song has profanity.
                    SONG_SWEAR_FREE if song is clean.
                    SONG_NOT_FOUND  if failure to reach server.

            (list): list containing swear words in order of appearance in the
                    song, based on lyrics provided.
    """
    tokens = lyrics.split()
    bad_found = []
    st = LancasterStemmer()

    test = None
    for word in tokens:
        w = word.strip('!,.?').lower()
        if st.stem(w) in bad_words:
            bad_found.append(w)
    if len(bad_found) > 0:
        test = SONG_HAS_SWEARS
    else:
        test = SONG_SWEAR_FREE
    return [test, bad_found ]


def get_lyrics(auth, api_path):
    """Find the Lyrics of a given song.

    given an api path for a specific song, return the lyrics from genius.

    Args:
        auth     (str): Genius API token
        api_path (str): path to song API

    Returns:
            (str): string containing song lyrics
    """
    # URL Is combination of genius API URL and the api path for a song
    url = GENIUS_URL + api_path

    # GET request
    response = requests.get(url, headers=auth)

    # Get json version
    json = response.json()
    path = json["response"]["song"]["path"]

    # Scrape using soup
    url = "http://genius.com" + path
    lyric_page = requests.get(url)
    html = BeautifulSoup(lyric_page.text, "html.parser")

    # Clean script tags
    [h.extract() for h in html('script')]

    # Return lyrics, these are tagged nicely in Genius
    lyrics = html.find("div", class_="lyrics").get_text()
    return lyrics

def run_tests(lyrics,bad_words):
    """Run all existing profanity tests and return results.

    Args:
        lyrics      (str): Song Lyrics
        bad_words   (str): loaded in list of bad words
    Returns:
            (list): list containing reports from each test
    """

    # Add new clean tests here
    test_list = [ clean_test_01,
                  clean_test_02 ]

    res = []
    for test in test_list:
        res.append( test(lyrics,bad_words)  )

    return res

def evaluate_tests(results):
    """Convert Test Results into a readable report.

    Given a list of results, converts into a readable report message.

    Args:
        results (str): unformatted results listings for each profanity test

    Returns:
            (str): Generated report
    """
    i = 1
    msg = ""
    swears = ""
    code   = ""
    for test in results:
        code = test_code(test[0],i)
        if test[0] == SONG_HAS_SWEARS:
            if i > 1:
                swears = " Song Contains: " + ", ".join(test[1])
            else:
                swears = " Song May Contain Swears, Check other Tests"
        #print(code)
        msg += code + swears + "\n"
        i += 1

    return msg

def test_code(code, number):
    """Convert each test code into a readable message.

    Given a code value and a test number, generate a readable report
    synopsis for each test. This synopsis will simply state whether a song
    passed or failed a given test.

    Args:
        code   (int): Code value corresponding to a test result
        number (int): Test Number

    Returns:
            (str): Generated synopsis for given test
    """
    if code == SONG_HAS_SWEARS:
        return "FAIL Profanity Test #" + str(number)
    elif code == SONG_SWEAR_FREE:
        return "PASS Profanity Test #" + str(number)
    else:
        return "Song Lyrics Not Found"

def generate_report(song,artist,lyrics,result):
    """Generate Final Lyrics Report.

    Combining all previous reporting features, this will generate a
    report containing the song name and artist, as well as
    the results from each test and the lyrics for the song.

    Args:
        song      (str): Song Name
        artist    (str): Song Artist
        lyrics    (str): Song Lyrics
        result   (list): List of (Unevaluated) Results

    Returns:
            (str): Generated report for a song
    """
    msg = ""
    msg += "Song   Name: " + song + "\n"
    msg += "Song Artist: " + artist + "\n\n"
    msg += evaluate_tests(result) + "\n\n"
    msg += "Song Lyrics: "
    msg += lyrics

    return msg


def get_api_path(auth, song_title, song_artist):
    """Find a song using Genius API and return an api path to it.

    Attempt to find a song on Genius using various API queries. If
    a song is found on the genius site, the path to the song is returned.
    This can be later used to return the song's lyrics.

    simliarity tests can be adjusted to fine tune accuracy of finding
    songs.

    Args:
        auth        (str): Genuis API token
        song_title  (str): Song name
        song_artist (str): Song artist

    Returns:
            (str): song's API path
    """
    url = GENIUS_URL + "/search"

    # First search: Search by song title
    data = {'q': song_title}
    response = requests.get(url, data=data, headers=auth)

    # Get JSON Data
    json = response.json()

    # Info will contain data for a "hit"
    info = None
    song_api_path = None

    # compare two strings
    a = None
    b = song_artist.lower()
    for hit in json["response"]["hits"]:
        a = hit["result"]["primary_artist"]["name"].lower()
        if similarity(a,b) >= 0.7:
            info = hit
            break
    if info:
        song_api_path = info["result"]["api_path"]
    else:
        # Second search: Reversed, search by artist
        data = {'q': song_artist}
        response = requests.get(url, data=data, headers=auth)
        json = response.json()
        info = None

        b = song_title.lower()
        for hit in json["response"]["hits"]:
            a = hit["result"]["title"].lower()
            if similarity(a,b) >= 0.7:
                info = hit
                break
        if info:
            song_api_path = info["result"]["api_path"]
    return song_api_path


def run(song,artist,bad_words,auth):
    """Run a report on a song, generating lyrics and potential swears.


    Args:
        song        (str): Song Name
        artist      (str): Song Artist
        bad_words  (list): List of Bad Words
        auth        (str): Genuis API token

    Returns:
            (str)    : Report containing found swears, and lyrics
            (boolean): True if runs without finding swears, False if swears found
    """
    api_path = get_api_path(auth, song, artist)
    report = ""
    lyrics = ""
    if api_path is not None:
        lyrics = get_lyrics(auth, api_path)
        result = run_tests(lyrics, bad_words)
        report = generate_report(song,artist,lyrics,result)
    else:
        report = "Song Lyrics Not Found"
        return report, True
    if report.count("FAIL") > 1:
        return report, False
    else:
        return report, True

def usage():
    """Print Usage Statement.

    Print the usage statement for running genius.py standalone.

    Returns:
        msg (str): Usage Statement.

    Example:

        >>> import genius
        >>> msg = genius.usage()
        >>> msg
        '<genius.py usage statement>'
    """
    msg = "genius.py usage:\n"
    msg = msg + "$ python genius.py \"<SONG_NAME>\" "
    msg = msg + "\"<SONG_NAME>\" "
    msg = msg + "\"<GENIUS_TOKEN>(optional)\" "
    return msg


if __name__ == "__main__":
    if(len(sys.argv) > 3):
        auth   = load_auth(sys.argv[3])
    elif(len(sys.argv) > 2):
        auth = load_auth()
    else:
        print(usage())
        sys.exit()

    song      = sys.argv[1]
    artist    = sys.argv[2]

    bad_words = load_profanity("../profanity.txt")

    msg, status = run(song,artist,bad_words,auth)
    print( msg, "Clean: ", status )
