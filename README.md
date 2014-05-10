Intake
===========
Version 0.1

Intake is a program designed to aid computer technicians in taking a computer
in with a little valuable knowledge. This program can be used to provide
the technician with a variety of information.

Usage
===========

intake [-v] [-s] [-o filename] [-i value1,value2]

intake [-v] [-s] [-o filename] [-i value1,value2]

Short Switch | Long Switch    | Description
-------------|----------------|--------------------------------------------------------------
-v           | --verbose      | Show all of the information that is logged on screen
             |                | By default, only the titles of the scans are outputed.
-s           | --silent       | Don't show any information on screen.
-o           | --output       | Choose a new path to output to output to.
             |                | The default path is "Logs/%datetime%.txt"         
-i           | --information  | Choose what information you want to be included in the logs.
             |                | Possible choices are listed below.
-h           | --help         | Show this help message.


Possible values for --information:

Name               | Description
-------------------|-------------------------------------------------------------------------
general            | Logs general system information from systeminfo.exe
antivirus          | Logs the currently registered antivirus product
keys               | Logs all product keys from ProduKey.exe
programs           | Logs all registered installed programs
drivers            | Logs all driver errors/warnings
failedservices     | Logs all services that are set to auto start but are not running
startup            | Logs all startup programs listed in msconfig
environment        | Logs all environment variables

Honarable mentions to Nirsoft for ProduKey -- www.nirsoft.net

License
===========

GNU GPL - v2
