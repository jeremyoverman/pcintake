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
class Log:
    def __init__(self, output, verbose, silent):
        """Handle all log events. Also handles printing to screen."""
        self.verbose = verbose
        self.silent = silent
        self.output = output
        self.buff = ""
    
    def addBlank(self):
        """Add a blank line to the log."""
        self.addLine("")
        
    def addTitle(self, text):
        """Add a title with an underline to the log."""
        underline = "=" * len(text)
        self.addBlank()
        title = "%s\n%s" % (text, underline)
        if not self.verbose and not self.silent:
            #By default, only print the title without underlines.
            print text
        self.addLine(title)
        self.addBlank()
    
    def addLine(self, text):
        """Add a line of text to the log."""
        final_text = "%s\n" % text
        self.buff += (final_text)
        if self.verbose:
            #If the verbose switch is on, print all lines to the screen.
            print text
    
    def addInformation(self, text):
        """Add information to the log in the form I: %information%."""
        self.addLine("I: %s" % text)
        
    def addError(self, text):
        """Add an error to the log in the form E: %error%."""
        self.addLine("E: %s" % text)
        
    def printBuffer(self):
        """Print the entire buffer to be written to the log. For debug purposes."""
        print self.buff
    
    def writeLog(self):
        """Write the buffer to the log file."""
        self.file = open(self.output, 'w')
        for char in self.buff:
            try:
                self.file.write(char.encode("utf8"))
            except: #Having trouble with some characters not encoding.
                self.file.write("?") 
        self.file.close()
