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

import _winreg as reg
import os

class Registry:
    def __init__(self):
        self.default_root = reg.HKEY_CURRENT_USER
        self.roots = {"HKEY_CLASSES_ROOT": reg.HKEY_CLASSES_ROOT,
                      "HKEY_CURRENT_USER": reg.HKEY_CURRENT_USER,
                      "HKEY_LOCAL_MACHINE": reg.HKEY_LOCAL_MACHINE,
                      "HKEY_USERS": reg.HKEY_USERS,
                      "HKEY_CURRENT_CONFIG": reg.HKEY_CURRENT_CONFIG
                      }
        self.search_results = []
    
    def parsePath(self, path, value=False):
        hkey = path.split("\\")[0][0:4]
        if hkey == "HKEY":
            root = self.roots[path.split("\\")[0]]
            path= path[path.find("\\")+1:]
        else:
            root = self.roots
        if value:
            value = path[path.rfind("\\")+1:]
            key = path[:path.rfind("\\")]
        else:
            key = path
        return (root, key, value)

    def getValue(self, path):
        root, key, value = self.parsePath(path, True)
        openkey = reg.OpenKeyEx(root, key, 0,  reg.KEY_READ | reg.KEY_WOW64_64KEY)
        result = reg.QueryValueEx(openkey, value)
        return result[0]
        
    def expandPath(self, path):
        return os.path.expandvars(path)
    
    def enumerate(self, path, type="keys"):
        keys_list = []
        root, key, value = self.parsePath(path)
        openkey = reg.OpenKeyEx(root, key, 0, reg.KEY_READ | reg.KEY_WOW64_64KEY)
        i = 0
        while True:
            try:
                if type == "keys":
                    keys_list.append(reg.EnumKey(openkey, i))
                elif type == "values":
                    keys_list.append(reg.EnumValue(openkey, i))
            except WindowsError:
                return keys_list
            else:
                i += 1
            
    def searchValues(self, root, term):
        self.search_results = []
        self.iterValues(root, term)
        return self.search_results
        
    def iterValues(self, root, term):
        sub_keys = self.enumerate(root)
        for key in sub_keys:
            current_key = root + "\\" + key
            values = self.enumerate(current_key, "values")
            for value in values:
                if value[0] == term:
                    self.search_results.append(current_key)
            self.iterValues(current_key, term)
            

if __name__ == "__main__":
    registry = Registry()
    #print registry.enumKeys("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Office\\15.0")
    print registry.searchValues("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Office", "DigitalProductID")