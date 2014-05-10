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
import regaccess, iekeys

if __name__ == '__main__':
    registry = regaccess.Registry()
    version = registry.getValue("HKEY_LOCAL_MACHINE\Software\Microsoft\Internet Explorer\Version").split(".")[0]
    if version == "9":
        for setting in iekeys.IE89:
            print setting, iekeys.IE89[setting][1]
            try:
                value = registry.getValue(iekeys.IE89[setting][1])
            except WindowsError as e:
                print "Error: %s" % e
            print "%s: %s" % (setting, value)
