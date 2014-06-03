from .. import getSubprocess

class Startup:
    def __init__(self, sql, verbose):
        self.sql = sql
        self.sql.createTable("startup", "Startup Processes", "Processes")

    def log(self):
        """Log all startup programs that show in msconfig.exe."""
        
        command = "WMIC startup get caption"
        output = getSubprocess(command)
        
        for line in output:
            if line.strip() != "Caption":
                self.sql.addValueToTable("startup", line.strip())