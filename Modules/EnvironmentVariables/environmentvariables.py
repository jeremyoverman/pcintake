import os

class Environment:
    def __init__(self, sql, verbose):
        self.sql = sql
        self.sql.createTable("environment", "Environment Variables", "Key", "Value")
    
    def log(self):
        """Log all environment variables."""
        
        env = os.environ
        values = []
        for var in env:
            values.append(var)
        for var in sorted(values):
            self.sql.addValueToTable("environment", var, env[var])