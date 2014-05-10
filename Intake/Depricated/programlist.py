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
import regaccess

class Programs:
    def __init__(self):
        self.path = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        self.registry = regaccess.Registry()
        self.keys = self.getKeys()
    
    def getKeys(self):
        keys = self.registry.enumKeys(self.path)
        return keys
    
    def getNames(self):
        i = 0
        names = []
        for key in self.keys:
            value = "%s\\%s\\DisplayName" % (self.path, key)
            try:
                name = self.registry.getValue(value)
            except WindowsError:
                name = "* " + key
            names.append(name)
            i += 1
        return names
            
    def logPrograms(self, log):
        log.addTitle("Installed Programs")
        log.addInformation("An asterisk (*) beside a name means there is no uninstaller information.")
        log.addBlank()
        names = sorted(self.getNames())
        for name in names:
            log.addInformation(name)
                
        
if __name__ == "__main__":
    programs = Programs()
    
