"""KTEQ-FM LOG FUNCTIONS.

This module contains most of the JSON data calls for the TeqBot project.
This has been done to consolidate a lot of the functions used in formatting
json data into messages to be sent via slack or other messaging systems.

Please visit http://python-guide-pt-br.readthedocs.io/en/latest/scenarios/json/
for more information on how to use json files with python3.

Example:

        $ python log.py "<JSON_FILE>"

Running this module from command line will try to generate a swear log report
from the given json file.

Todo:
    * Add additional logs that can be read and submitted.

.. _TeqBot GitHub Repository:
   https://github.com/kteq-fm/kteq-teqbot

.. _KTEQ-FM Website:
   http://www.kteq.org/

"""

import sys
import json

LOG_SWEAR = 1

def compare_json(json1,json2):
    """Compare Two JSON data structs to check if they're identical.

    Args:
        json1 (dict): json data
        json2 (dict): json data

    Returns:
        (boolean): True if identical, False if not
    """
    # Iterate Through First
    for key, value in json1.items():
        if key not in json2:
            return False
        else:
            if value != json2[key]:
                return False

    # Iterate Through Last
    for key, value in json2.items():
        if key not in json1:
            return False
        else:
            if value != json1[key]:
                return False

    # Must be identical
    return True

def read_json(filename):
    """Read JSON file and store to a variable.

    Args:
        filename (str): file name (input)

    Returns:
        (dict): data in json format

    Example:

        >>> import log
        >>> data = log.read_json("test.json")
    """
    with open(filename) as j:
        return json.load(j)

def write_json(data, filename):
    """Write JSON file from a json data variable.

    Args:
        data     (dict): JSON data
        filename (str) : file name (output)

    Returns:
        None (writes file)

    Example:

        >>> import log
        >>> d = { "Coolness Factor": 0 }
        >>> data = log.write_json(d,"test.json")
    """
    with open(filename, 'w') as j:
        json.dump(data, j)

def validate(data,log_type):
    """Ensure json data has all the important entry fields

    Args:
        data     (dict): JSON data for swear log
        log_type  (int): Specified log type
    Returns:
        (boolean): True if valid, False otherwise.

    """

    if log_type is LOG_SWEAR:
        fields = ["date", "time", "song title",
                  "song artist", "song composer",
                  "show name", "report"]
        for f in fields:
            if f not in data:
                return False
            return True
    return False

def generate_swear_log(data):
    """Generate Swear Log from JSON data

    Args:
        data    (dict): JSON data for swear log
    Returns:
        msg (str): Swear Log.

    """
    msg = ""

    if validate(data, LOG_SWEAR):
        msg += "```\n"
        msg += "SWEAR LOG SUBMISSION FROM " + data['show name'] + ":\n\n"
        msg += "Date         \t" + data['date']           + "\n"
        msg += "Time         \t" + data['time']           + "\n"
        msg += "Song     Name\t" + data['song title']     + "\n"
        msg += "Song   Artist\t" + data['song artist']    + "\n"
        msg += "Song Composer\t" + data['song composer']  + "\n"
        msg += "\n\n"

        msg += "Report:    \t" + data['report']
        msg += "```"

    return msg

def usage():
    """Print Usage Statement.

    Print the usage statement for running log.py standalone.

    Returns:
        msg (str): Usage Statement.

    Example:

        >>> import log
        >>> msg = log.usage()
        >>> msg
        '<log.py usage statement>'
    """
    msg = "log.py usage:\n"
    msg = msg + "$ python log.py \"<JSON_FILE>\" "
    return msg


if __name__ == "__main__":
    if(len(sys.argv) > 1):
        filename = sys.argv[1]
    else:
        print(usage())
        sys.exit()

    # read in json
    j = read_json(filename)

    l = generate_swear_log(j)

    print(l)
