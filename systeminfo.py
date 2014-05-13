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
import os, wmi
from subprocess import Popen, PIPE

class ProductKey:
    def __init__(self):
        """Log all product keys from ProduKey.exe"""
        
        self.produkey = "ProduKey/ProduKey.exe"
        self.switches = "/scomma \"\""
        self.keys = self.getKeys()
        
    def logKeys(self, log):
        """Log the keys."""
        
        log.addTitle("Product Keys")
        for key in self.keys:
            log.addLine("%s: %s" % (key, self.keys[key]))
        
    def getKeys(self):
        """Get all keys from ProduKey.exe"""
        
        output = Popen(self.produkey + " " + self.switches, stdout=PIPE).stdout.read()
        keys = {}
        for line in output.split("\n"):
            split = line.split(",")
            if len(split) == 7:
                name = split[0]
                key = split[2]
                keys[name] = key
        return keys

class powerConfig:
    def __init__(self):
        """Get all power configuration information. Not working correctly."""
        
        self.command = "powercfg"
        self.command_output = Popen(self.command + " " + "/Q", stdout=PIPE).stdout.readlines()
        self.options = {}
        self.current_subgroup = None
        self.current_pwroption = None
        self.index = 0
        
        #for line in self.command_output:
        #    print line
        self.makeRuleTree()
        
    def getCurrentPlan(self):
        """Get the name of the current power plan."""
        
        output = Popen(self.command + " " + "/L", stdout=PIPE).stdout.readlines()
        for line in output:
            line = line.strip()
            if len(line) > 0:
                if line[-1] == "*":
                    plan = line[line.find("(")+1:line.find(")")]
        return plan
    
    def getKeyValue(self, line):
        """Get the value of a key value pair in a line."""
        
        key = line.split(":")[0]
        value = line.split(":")[1][1:]
        return (key, value)
    
    def getPossibilities(self):
        """Get possible values for each power option."""
        
        self.index -= 1
        possibilities = {}
        current = None
        while True:
            line = self.command_output[self.index].strip()
            key, value = self.getKeyValue(line)
            if key == "Possible Setting Index":
                value = int(value)
                possibilities[value] = None
                current = value
                self.index += 1
            elif key == "Possible Setting Friendly Name":
                possibilities[current] = value
                self.index += 1
            else:
                break
        return possibilities
        
    def makeRuleTree(self):
        """Iterable function to get all power option values."""
        
        try:
            line = self.command_output[self.index].strip()
            self.index += 1
        except IndexError:
            return
        if len(line) > 0:
            key, value = self.getKeyValue(line)
            if key == "Subgroup GUID":
                guid = value.split()[0]
                if value.find("(") == -1:
                    name = "NO NAME"
                else:
                    name = value[value.find("(")+1:-1]
                self.current_subgroup = guid
                self.options[guid] = {"name": name}
                #print guid, name, "(%s)" % line
            elif key == "Power Setting GUID":
                guid = value.split()[0]
                if value.find("(") == -1:
                    name = "NO NAME"
                else:
                    name = value[value.find("(")+1:-1]
                #print "  " + guid, name
                self.current_pwroption = guid
                self.options[self.current_subgroup][guid] = {
                                                              "name": name,
                                                              "units": None,
                                                              "possibilities": None,
                                                              "AC": None,
                                                              "DC": None
                                                             }
            else:
                if key == "Possible Setting Index":
                    self.options[self.current_subgroup][self.current_pwroption]["possibilities"] = self.getPossibilities()
                elif key == "Possible Settings units":
                    self.options[self.current_subgroup][self.current_pwroption]["units"] = value
                elif key == "Current AC Power Setting Index":
                    self.options[self.current_subgroup][self.current_pwroption]["AC"] = int(value, 16)
                elif key == "Current DC Power Setting Index":
                    self.options[self.current_subgroup][self.current_pwroption]["DC"] = int(value, 16)
                    
            self.makeRuleTree()
        else:
            self.makeRuleTree()
        
    def logRules(self, log):
        """Write all of the power options to the log."""
        
        log.addTitle("Power Options")
        print self.options
        for group in self.options:
            power_options = self.options[group]
            if power_options:
                log.addLine(power_options["name"])
                for setting in power_options:
                    if setting != "name":
                        possibilities = power_options[setting]["possibilities"]
                        ac = power_options[setting]["AC"]
                        dc = power_options[setting]["DC"]
                        units = power_options[setting]["units"] 
                        #print "  " + power_options[setting]["name"]
                        if possibilities == None:
                            log.addLine("    AC: %s %s" % (ac, units))
                            log.addLine("    DC: %s %s" % (ac, units))
                        else:
                            log.addLine("    AC: %s" % (possibilities[ac]))
                            log.addLine("    DC: %s" % (possibilities[dc]))

        
class Information:
    def __init__(self):
        self.c = wmi.WMI()
        
    def logPrograms(self, log):
        """Log all registered installed programs."""
        
        log.addTitle("Installed Programs")
        
        command = "wmic product get description"
        output = Popen(command, stdout=PIPE).stdout.readlines()
        
        for line in output:
            if line.find("Description") < 0:
                log.addLine(line.strip())
        
    def parseSystemInfoCSV(self, csv):
        """Parse the CSV results from the systeminfo.exe command."""
        
        values = []
        
        buff = ""
        in_word = False
        for x in csv:
            if x == "\"":
                if in_word: in_word = False
                else: in_word = True
            elif in_word:
                buff += x
            else:
                values.append(buff)
                buff = ""
        return values
    
    def logSystemInfo(self, log):
        """Log system info from systeminfo.exe."""
        log.addTitle("General System Information")
        information = self.getSystemInfo()
        tolog = [
                 "Host Name",
                 "OS Name",
                 "OS Version",
                 "System Manufacturer",
                 "System Model",
                 "Processor(s)",
                 "Total Physical Memory",
                 "Original Install Date",
                 "BIOS Version"
                 ]
        for item in tolog:
            log.addLine("%s: %s" % (item, information[item]))
        log.addLine("Serial Number: " + self.getSerial())
            
    def getSerial(self):
        """Get the serial number of the computer if available."""
        
        command = "wmic /namespace:\\\\root\\cimv2 path Win32_SystemEnclosure get SerialNumber"
        output = Popen(command, stdout=PIPE).stdout.readlines()
        
        serial = "Not Found"
        
        for line in output:
            if len(line.strip()) > 0:
                if line.find("SerialNumber") < 0:
                    serial = line.strip()
        return serial
        
    def logFailedServices(self, log):
        """Log all services that were supposed to automatically start but are not running."""
        
        log.addTitle("Failed Services")
        command = "wmic service where \"State = 'Stopped' and StartMode = 'Auto'\" get Caption"
        output = Popen(command, stdout=PIPE).stdout.readlines()
        
        for line in output:
            if len(line.strip()) > 0 and line.find("Caption") < 0:
                log.addLine(line.strip())
        
    def getSystemInfo(self):
        """Get system information from systeminfo.exe."""
        
        command = "systeminfo /FO csv"
        output = Popen(command, stdout=PIPE).stdout.readlines()
        
        keys = self.parseSystemInfoCSV(output[0])
        values = self.parseSystemInfoCSV(output[1])
        information = {}
        
        i = 0
        for key in keys:
            information[key] = values[i]
            i += 1
        return information
        
            
    def logEnvironment(self, log):
        """Log all environment variables."""
        
        log.addTitle("Environment Variables")
        env = os.environ
        values = []
        for var in env:
            values.append(var)
        for var in sorted(values):
            log.addLine("%s: %s" % (var, env[var]))
    
    def logStartup(self, log):
        """Log all startup programs that show in msconfig.exe."""
        
        log.addTitle("Startup Processes")
        command = "WMIC startup get caption"
        output = Popen(command, stdout=PIPE).stdout.readlines()
        
        for line in output:
            if line.strip() != "Caption":
                log.addLine(line.strip())
            
    def logAntivirus(self, log):
        """Log the currently registered antivirus program."""
        
        log.addTitle("Antivirus")
        command = "WMIC /Node:localhost /Namespace:\\\\root\\SecurityCenter2 Path AntiVirusProduct Get displayName /Format:List"
        output = Popen(command, stdout=PIPE).stdout.readlines()
        
        name = "No Antivirus"
        
        for line in output:
            line = line.strip()
            if len(line) > 0:
                name = line.split("=")[1]
        log.addLine(name)
    
    def logBadDrivers(self, log):
        """Log all drivers with errors (would show with abnormal icons in device manager)."""
        
        log.addTitle("Driver Errors")
        command = 'wmic /namespace:\\\\root\\cimv2 path win32_PnPEntity where "ConfigManagerErrorCode <> 0" get Caption,DeviceID'
        output = Popen(command, stdout=PIPE).stdout.readlines()
        
        for line in output:
            if len(line.strip()) > 0:
                log.addLine(line)
                
if __name__ == "__main__":
    import cleanlog
    information = Information()

    
