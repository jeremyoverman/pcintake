from Modules.Antivirus.antivirus import Antivirus

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

class Information:
    def __init__(self, log):
        self.log = log
        
    def logAntivirus(self, verbose):
        if verbose:
            print "Logging Registered Antivirus"
        antivirus = Antivirus(self.log)
        antivirus.logAntivirus()

        
if __name__ == "__main__":
    import log
    sql = log.SQL()
    information = Information(sql)
    information.logAntivirus(True)
    
    