#!/usr/bin/python

# =============================================================================
# This is the main function for generating the KTEQ-FM Quarterly Issues Report.
# =============================================================================

import functions

#find out the current quarter
quarter = input("Enter the quarter of the report to be generated: ")

#get the logs into a list of named tuples
logs = functions.readcsv()

#actually generate the report
functions.generatedocx(logs,quarter)