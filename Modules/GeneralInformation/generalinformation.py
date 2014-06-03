from .. import getSubprocess

class GeneralInformation:
    def __init__(self, sql, verbose):
        self.sql = sql
        self.sql.createTable("general", "General Information", "Key", "Value")
    
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

    def log(self):
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
            self.sql.addValueToTable("general", item, information[item])
        self.sql.addValueToTable("general", "Serial Number", self.getSerial())