from .. import getSubprocess

class InstalledPrograms:
    def __init__(self, sql, verbose):
        self.sql = sql
        self.sql.createTable("programs", "Installed Programs", "Installed Programs")
        
    def log(self):
        """Log all registered installed programs."""
        
        command = "wmic product get description"
        output = getSubprocess(command)
        
        for line in output:
            if line.find("Description") < 0:
                program = line.strip()
                self.sql.addValueToTable("programs", program)