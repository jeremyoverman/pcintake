from .. import getSubprocess

class FailedServices:
    def __init__(self, sql, verbose):
        self.sql = sql
        sql.createTable("failedservices", "Failed Services", "Failed Services")
    
    def log(self):
        """Log all services that were supposed to automatically start but are not running."""
        
        command = "wmic service where \"State = 'Stopped' and StartMode = 'Auto'\" get Caption"
        output = getSubprocess(command)
        
        for line in output:
            if len(line.strip()) > 0 and line.find("Caption") < 0:
                self.sql.addValueToTable("failedservices", line.strip())