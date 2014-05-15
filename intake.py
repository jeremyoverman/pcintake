#-------------------------------------------------------------------------------
# Copyright (c) 2014 Jeremy Overman.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v2.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# 
# Contributors:
#     Jeremy Overman - initial API and implementation
#-------------------------------------------------------------------------------
import systeminfo
import log
import sys, time, os

helpmessage = """
Usage:

intake [-v] [-s] [-o filename] [-i value1,value2]

-v --verbose        Show all of the information that is logged on screen
                    By default, only the titles of the scans are outputed.

-o --output         Choose a new path to output to output to.
                    The default path is "Logs/%datetime%.txt"
                   
-i --information    Choose what information you want to be included in the logs.
                    Possible choices are listed below.
                   
-h --help           Show this help message.

Possible values for --information:

general             Logs general system information from systeminfo.exe
antivirus           Logs the currently registered antivirus product
keys                Logs all product keys from ProduKey.exe
programs            Logs all registered installed programs
drivers             Logs all driver errors/warnings
failedservices      Logs all services that are set to auto start but are not running
startup             Logs all startup programs listed in msconfig
environment         Logs all environment variables
"""

class Main():
    def __init__(self):
        """Sets all of the default options, then parses command line arguments"""
        
        self.initOptions()
        self.initScanners()
        self.i = 0
        self.args = sys.argv[1:]
        
        self.flags = {"-v": self.verbose,
                 "--verbose": self.verbose,
                 "-o": self.output,
                 "-output": self.output,
                 "-s": self.silent,
                 "--silent": self.silent,
                 "-i": self.information,
                 "--information": self.information}
        
        self.iterateArguments()
        
    def initOptions(self):
        """Sets the default options as self.options"""
        
        self.time = time.asctime()
        #Use this filename when compiling
        filename = os.path.join(os.path.dirname(sys.executable), "Logs", "Log - %s.html" %  self.time.replace(":", "-"))
        
        #Use this filename when testing/coding
        #filename = "Logs/Log - %s.html" % self.time.replace(":", "-")
        
        self.options = {"verbose": False,
                        "output": filename,
                        "silent": False,
                        "information": ["general",
                                        "antivirus",
                                        "keys",
                                        "programs",
                                        "drivers",
                                        "failedservices",
                                        "startup",
                                        "environment"]
                       }
    
    def initScanners(self):
        """Defines the default information to be gathered and logged."""
        self.scanners = {
                         "general": information.logSystemInfo,
                         "antivirus": information.logAntivirus,
                         "keys": information.logProductKeys,
                         "programs": information.logPrograms,
                         "drivers": information.logBadDrivers,
                         "failedservices": information.logFailedServices,
                         "startup": information.logStartup,
                         "environment": information.logEnvironment,
                         #power.logRules(log)
                        } 
        
        
    def iterateArguments(self):
        """Iterates through all of the command line arguements.
        
        self.i is used as the iterator and each function can manipulate it
        if, for instance, it requires the next argument as input for the switch."""
        
        while True:
            try: arg = self.args[self.i]
            except: break
            if arg in self.flags:
                command = self.flags[arg]
                command()
            else:
                self.help(arg)
            self.i += 1
    
    def help(self, arg=None):
        if arg:
            print "\nInvalid argument: %s" % arg
        print helpmessage
        sys.exit(2)
    
    def verbose(self):
        """Sets the "verbose" option to True"""
        
        self.options["verbose"] = True
        
    def silent(self):
        """Sets the "silent" option to True"""
        
        self.options["silent"] = True

    def output(self):
        """Assigns a new log output file"""
        
        self.i += 1
        filename = self.args[self.i]
        self.options["output"] = filename
    
    def information(self):
        """Determines what information should be gathered and logged."""
        
        self.i += 1
        try:
            scans = self.args[self.i]
            self.options["information"] = []
            for scan in scans.split(","):
                if scan in self.scanners:
                    self.options["information"].append(scan)
                else:
                    self.help()
                    break
        except IndexError:
            self.help()
    
    def runScanner(self):
        """Gather and log all requested information."""
        
        for scan in self.options["information"]:
            self.scanners[scan](self.options["verbose"])
            #try:
            #    self.scanners[scan]()
            #except:
            #    #Fail on any errors and report the error, though run the other scans still
            #    e = sys.exc_info()[1]
            #    print "Scan Failed! [%s]" % e
        
        #log.writeLog()

if __name__ == "__main__":
    #power = systeminfo.powerConfig() #Not working
    
    sql = log.SQL()
    logger = log.Log(sql) 
    information = systeminfo.Information(sql)
    main = Main()
    
    main.runScanner()
    logger.writeLog(main.options["output"])
