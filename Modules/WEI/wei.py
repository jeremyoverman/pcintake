import os, glob
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
            