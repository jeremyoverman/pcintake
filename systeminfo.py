import os
from subprocess import Popen, PIPE
import regaccess

def getSubprocess(command):
    proc = Popen(command, stdout=PIPE, stderr=None)
    output = [''.join([x for x in y if ord(x) < 128]) for y in proc.stdout.readlines()]
    return output

class ProductKeys:
    def __init__(self, log):
        self.log = log
        self.log.createTable("keys", "Product Keys", "Product Name", "Product Key")
        self.registry = regaccess.Registry()
        
    def DecodeKey(self, rpk):
        rpkOffset = 52
        i = 28
        szPossibleChars = "BCDFGHJKMPQRTVWXY2346789"
        szProductKey = ""
        
        while i >= 0:
            dwAccumulator = 0
            j = 14
            while j >= 0:
                dwAccumulator = dwAccumulator * 256
                d = rpk[j+rpkOffset]
                if isinstance(d, str):
                    d = ord(d)
                dwAccumulator = d + dwAccumulator
                rpk[j+rpkOffset] = (dwAccumulator / 24) if (dwAccumulator / 24) <= 255 else 255 
                dwAccumulator = dwAccumulator % 24
                j = j - 1
            i = i - 1
            szProductKey = szPossibleChars[dwAccumulator] + szProductKey
            
            if ((29 - i) % 6) == 0 and i != -1:
                i = i - 1
                szProductKey = "-" + szProductKey
                
        return szProductKey
    
    def getInformation(self, key):
        product_id = self.registry.getValue(key + "\\DigitalProductId")
        try:
            product_name = self.registry.getValue(key + "\\ProductName")
        except WindowsError:
            product_name = self.registry.getValue(key + "\\ProductNameNonQualified")
        product_key = self.DecodeKey(list(product_id))
        return (product_name, product_key)
    
    def logWindowsKey(self):
        product_name, product_key = self.getInformation("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion")
        self.log.addValueToTable("keys", product_name, product_key)
        
    def logOfficeKeys(self):
        reg_keys = self.registry.searchValues("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Office", "DigitalProductID")
        for reg_key in reg_keys:
            product_name, product_key = self.getInformation(reg_key)
            self.log.addValueToTable("keys", product_name, product_key)
            
        return (product_name, product_key)
    
    def logKeys(self):
        self.logWindowsKey()
        self.logOfficeKeys()

class PowerConfig:
    def __init__(self):
        """Get all power configuration information. Not working correctly."""
        
        self.command = "powercfg"
        self.command_output = getSubprocess(self.command + " " + "/Q", stdout=PIPE)
        self.options = {}
        self.current_subgroup = None
        self.current_pwroption = None
        self.index = 0
        
        #for line in self.command_output:
        #    print line
        self.makeRuleTree()
        
    def getCurrentPlan(self):
        """Get the name of the current power plan."""
        
        output = getSubprocess(self.command + " " + "/L", stdout=PIPE)
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

class InstalledPrograms:
    def __init__(self, log):
        self.log = log
        self.log.createTable("programs", "Installed Programs", "Installed Programs")
        
    def logPrograms(self):
        """Log all registered installed programs."""
        
        command = "wmic product get description"
        output = getSubprocess(command)
        
        
        for line in output:
            if line.find("Description") < 0:
                program = line.strip()
                self.log.addValueToTable("programs", program)

class GeneralInformation:
    def __init__(self, log):
        self.log = log
        self.log.createTable("general", "General Information", "Key", "Value")
    
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

    def getSerial(self):
        """Get the serial number of the computer if available."""
        
        command = "wmic /namespace:\\\\root\\cimv2 path Win32_SystemEnclosure get SerialNumber"
        output = getSubprocess(command)
        
        serial = "Not Found"
        
        for line in output:
            if len(line.strip()) > 0:
                if line.find("SerialNumber") < 0:
                    serial = line.strip()
        return serial
    
            
    def getSystemInfo(self):
        """Get system information from systeminfo.exe."""
        
        command = "systeminfo /FO csv"
        output = getSubprocess(command)
        
        keys = self.parseSystemInfoCSV(output[0])
        values = self.parseSystemInfoCSV(output[1])
        information = {}
        
        i = 0
        for key in keys:
            information[key] = values[i]
            i += 1
        return information

    def logSystemInfo(self):
        """Log system info from systeminfo.exe."""
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
            self.log.addValueToTable("general", item, information[item])
        self.log.addValueToTable("general", "Serial Number", self.getSerial())
        
class FailedServices:
    def __init__(self, log):
        self.log = log
        log.createTable("failedservices", "Failed Services", "Failed Services")
    
    def logFailedServices(self):
        """Log all services that were supposed to automatically start but are not running."""
        
        command = "wmic service where \"State = 'Stopped' and StartMode = 'Auto'\" get Caption"
        output = getSubprocess(command)
        
        for line in output:
            if len(line.strip()) > 0 and line.find("Caption") < 0:
                self.log.addValueToTable("failedservices", line.strip())

class Environment:
    def __init__(self, log):
        self.log = log
        log.createTable("environment", "Environment Variables", "Key", "Value")
    
    def logEnvironment(self):
        """Log all environment variables."""
        
        env = os.environ
        values = []
        for var in env:
            values.append(var)
        for var in sorted(values):
            self.log.addValueToTable("environment", var, env[var])

class Startup:
    def __init__(self, log):
        self.log = log
        self.log.createTable("startup", "Startup Processes", "Processes")

    def logStartup(self):
        """Log all startup programs that show in msconfig.exe."""
        
        command = "WMIC startup get caption"
        output = getSubprocess(command)
        
        for line in output:
            if line.strip() != "Caption":
                self.log.addValueToTable("startup", line.strip())

class Antivirus:
    def __init__(self, log):
        self.log = log
        self.log.createTable("antivirus", "Registered Antivirus", "Registered Antivirus")

    def logAntivirus(self):
        """Log the currently registered antivirus program."""
        
        command = "WMIC /Node:localhost /Namespace:\\\\root\\SecurityCenter2 Path AntiVirusProduct Get displayName /Format:List"
        output = getSubprocess(command)
        
        name = "No Antivirus"
        
        for line in output:
            line = line.strip()
            if len(line) > 0:
                name = line.split("=")[1]
        self.log.addValueToTable("antivirus", name)

class BadDrivers:
    def __init__(self, log):
        self.log = log
        self.log.createTable("drivers", "Driver Errors", "Driver Errors")
    
    def logBadDrivers(self):
        """Log all drivers with errors (would show with abnormal icons in device manager)."""

        command = 'wmic /namespace:\\\\root\\cimv2 path win32_PnPEntity where "ConfigManagerErrorCode <> 0" get Caption'
        output = getSubprocess(command)
        
        baddrivers = []
        
        for line in output:
            if len(line.strip()) > 0:
                baddrivers.append(line)
        if len(baddrivers) > 0:
            for driver in baddrivers:
                self.log.addValueToTable("drivers", driver)
        else:
            self.log.addValueToTable("drivers", "No driver errors")

class Information:
    def __init__(self, log):
        self.log = log
        
    def logProductKeys(self, verbose):
        if verbose:
            print "Logging Keys"
        productkeys = ProductKeys(self.log)
        productkeys.logKeys()
        
    def logPrograms(self, verbose):
        if verbose:
            print "Logging Installed Programs"
        programs = InstalledPrograms(self.log)
        programs.logPrograms()
        
    def logSystemInfo(self, verbose):
        if verbose:
            print "Logging System Information"
        general = GeneralInformation(self.log)
        general.logSystemInfo()
            
    def logFailedServices(self, verbose):
        if verbose:
            print "Logging Failed Services"
        failedservices = FailedServices(self.log)
        failedservices.logFailedServices()
        
    def logEnvironment(self, verbose):
        if verbose:
            print "Logging Environment Variables"
        environment = Environment(self.log)
        environment.logEnvironment()
    
    def logStartup(self, verbose):
        if verbose:
            print "Logging Startup Programs"
        startup = Startup(self.log)
        startup.logStartup()
            
    def logAntivirus(self, verbose):
        if verbose:
            print "Logging Registered Antivirus"
        antivirus = Antivirus(self.log)
        antivirus.logAntivirus()
    
    def logBadDrivers(self, verbose):
        if verbose:
            print "Logging Driver Errors"
        baddrivers = BadDrivers(self.log)
        baddrivers.logBadDrivers()
                        
if __name__ == "__main__":
    import log
    information = Information()


    
