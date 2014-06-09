import os, glob, wx
import xml.etree.ElementTree as ET

class WindowsEI:
    def __init__(self, sql, verbose):
        self.sql = sql
        self.sql.createTable("wei", "WEI Scores", "Assessment", "Score")
        
        windir = os.path.expandvars("%windir%")
        weidir = os.path.join(windir, "Performance", "WinSAT", "DataStore")
        formals = glob.iglob(os.path.join(weidir, '*Formal.Assessment*'))
        self.formal = max(formals, key=os.path.getctime)
        self.whitelist = ["SystemScore",
                          "MemoryScore",
                          "CpuScore",
                          "GraphicsScore",
                          "GamingScore",
                          "DiskScore"]
        
    def log(self):
        tree = ET.parse(self.formal)
        root = tree.getroot()
        WinSPR = root.find("WinSPR")
        for child in WinSPR:
            if child.tag in self.whitelist:
                self.sql.addValueToTable("wei", child.tag[:-5], child.text)

class GUI(wx.Panel):
    def __init__(self, parent, table, colnames):
        wx.Panel.__init__(self, parent)
        self.rdict, self.results = self.tableToDict(table)
        self.bold_font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        
        self.results_table = self.createTable()
        
        self.SetSizerAndFit(self.results_table)
        
    def tableToDict(self, table):
        rdict = {}
        for row in table:
            rdict[row[0]] = row[1]
        results = (
                      ("Component",
                       "What is rated",
                       "Subscore"
                      ),
                      ("Processor",
                       "Calculations per second",
                       rdict["Cpu"]
                      ),
                      ("Memory (RAM)",
                       "Memory operations per second",
                       rdict["Memory"]
                      ),
                      ("Graphics",
                       "Desktop performance for Windows Aero",
                       rdict["Graphics"]
                      ),
                      ("Gaming graphics",
                       "3D business and gaming graphics\nperformance",
                       rdict["Gaming"]
                      ),
                      ("Primary hard disk",
                       "Disk data transfer rate",
                       rdict["Disk"]
                      )
                   )
        return (rdict, results)
    
    def createTable(self):
        grid = wx.GridBagSizer(10, 20)
        
        ri = 0
        for row in self.results:
            ci = 0
            for col in row:
                text = wx.StaticText(self, label=col)
                if ri == 0 or ci == 0:
                    text.SetFont(self.bold_font)
                print (ri, ci)
                grid.Add(text, (ri, ci))
                ci += 1
            ri += 1
        self.CreateBaseScore(grid)
        
        return grid
    
    def CreateBaseScore(self, grid):
        header = wx.StaticText(self, label="Base Score")
        header.SetFont(self.bold_font)
        
        basescore = wx.StaticText(self, label=self.rdict["System"])
        base_font = wx.Font(42, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        basescore.SetFont(base_font)
        
        description = wx.StaticText(self, label="Determined by\nlowest subscore")
        
        grid.Add(header, (0,3))
        grid.Add(basescore, (1,3), (2,1))
        grid.Add(description, (3,3))

if __name__ == "__main__":
    table = [('System', '4.5'), ('Memory', '5.9'), ('Cpu', '6.9'),
             ('Graphics', '4.5'), ('Gaming', '4.8'), ('Disk', '7.9')]
    colnames = ['a', 'b']
    
    app = wx.App()
    
    frame = wx.Frame(None, -1, 'PCIntake', size=(640,480))
    #panel = wx.Panel(frame)
    
    gui = GUI(frame, table, colnames)
    frame.Show()
    
    app.MainLoop()
    