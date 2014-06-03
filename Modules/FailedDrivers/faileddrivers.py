from .. import getSubprocess

class BadDrivers:
    def __init__(self, sql, verbose):
        self.sql = sql
        self.sql.createTable("drivers", "Driver Errors", "Driver Errors")
    
    def log(self):
        """Log all drivers with errors (would show with abnormal icons in device manager)."""

        command = 'wmic /namespace:\\\\root\\cimv2 path win32_PnPEntity where "ConfigManagerErrorCode <> 0" get Caption'
        output = getSubprocess(command)
        
        baddrivers = []
        
        for line in output:
            if len(line.strip()) > 0:
                baddrivers.append(line)
        if len(baddrivers) > 0:
            for driver in baddrivers:
                self.sql.addValueToTable("drivers", driver)
        else:
            self.sql.addValueToTable("drivers", "No driver errors")
