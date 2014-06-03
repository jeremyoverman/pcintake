from .. import getSubprocess    

class Antivirus:
    def __init__(self, sql, verbose):
        self.sql = sql
        self.sql.createTable("antivirus", "Registered Antivirus", "Registered Antivirus")
        
    def log(self):
        """Log the currently registered antivirus program."""
        
        command = "WMIC /Node:localhost /Namespace:\\\\root\\SecurityCenter2 Path AntiVirusProduct Get displayName /Format:List"
        output = getSubprocess(command)
        
        name = "No Antivirus"
        
        for line in output:
            line = line.strip()
            if len(line) > 0:
                name = line.split("=")[1]
        self.sql.addValueToTable("antivirus", name)