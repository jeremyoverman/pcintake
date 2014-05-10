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
import platform, os
import cleanlog, regaccess, programlist

class Clean:
    def __init__(self):
        self.operatingsystem = "%s %s" % (platform.system(), platform.release())
        self.directories = [
                            ["dir", "Temporary Files", os.getenv("temp")],
                            ["key", "Internet Cache", "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders\Cache"],
                            ["key", "Cookies", "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders\Cookies"],
                            ["key", "History", "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders\History"]                            
                            ]
        
        #self.runCleaner()
        
        
    def getDirectorySize(self, path = '.'):
        total_size = 0
        number_of_files = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                total_size += os.path.getsize(fp)
                number_of_files += 1
        return (total_size / (1024 ** 2), number_of_files)
    
    def deleteDirectoryContents(self, directory):
        errors = {}
        size, files = self.getDirectorySize(directory)
        log.addInformation("%s (%sMB) files to remove." % (files, size))
        for root, dirs, files in os.walk(directory):
            for f in files:
                try:
                    full_path = os.path.join(root, f)
                    os.remove(full_path)
                except WindowsError as e:
                    errors[full_path] = e.strerror
                    log.addError("%s: %s" % (e.strerror, full_path))
            for d in dirs:
                try:
                    full_path = os.path.join(root, d)
                    os.rmdir(full_path)
                except WindowsError as e:
                    errors[full_path] = e.strerror
                    log.addError("%s: %s" % (e.strerror, full_path))
        size, files = self.getDirectorySize(directory)
        log.addInformation("%s (%sMB)files left." % (files, size))
        return errors
        
    def runCleaner(self):
        for item in self.directories:
            type, name, path = item[0], item[1], item[2]
            log.addTitle(name)
            if type == "dir":
                self.deleteDirectoryContents(path)
            elif type == "key":
                rel_path = registry.getValue(path)
                self.deleteDirectoryContents(registry.expandPath(rel_path))
        
if __name__ == "__main__":
    log = cleanlog.Log()
    registry = regaccess.Registry()
    programs = programlist.Programs()
    programs.writeProgramsToLog(log)
    log.writeLog()
    clean = Clean()
