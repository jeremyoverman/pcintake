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
f = open("test.txt", 'rw')
for line in f.readlines():
    print line
