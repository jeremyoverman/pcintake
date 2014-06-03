import regaccess

class ProductKeys:
    def __init__(self, sql, verbose):
        self.sql = sql
        self.sql.createTable("keys", "Product Keys", "Product Name", "Product Key")
        self.registry = regaccess.Registry()
        
    def DecodeKey(self, rpk):
        rpkOffset = 52
        i = 28
        szPossibleChars = "BCDFGHJKMPQRTVWXY2346789"
        szProductKey = ""
        
        while i >= 0:
            dwAccumulator = 0
            j = 14
            while j >= 0:
                dwAccumulator = dwAccumulator * 256
                d = rpk[j+rpkOffset]
                if isinstance(d, str):
                    d = ord(d)
                dwAccumulator = d + dwAccumulator
                rpk[j+rpkOffset] = (dwAccumulator / 24) if (dwAccumulator / 24) <= 255 else 255 
                dwAccumulator = dwAccumulator % 24
                j = j - 1
            i = i - 1
            szProductKey = szPossibleChars[dwAccumulator] + szProductKey
            
            if ((29 - i) % 6) == 0 and i != -1:
                i = i - 1
                szProductKey = "-" + szProductKey
                
        return szProductKey
    
    def getInformation(self, key):
        product_id = self.registry.getValue(key + "\\DigitalProductId")
        try:
            product_name = self.registry.getValue(key + "\\ProductName")
        except WindowsError:
            product_name = self.registry.getValue(key + "\\ProductNameNonQualified")
        product_key = self.DecodeKey(list(product_id))
        return (product_name, product_key)
    
    def logWindowsKey(self):
        product_name, product_key = self.getInformation("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion")
        self.sql.addValueToTable("keys", product_name, product_key)
        
    def logOfficeKeys(self):
        reg_keys = self.registry.searchValues("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Office", "DigitalProductID")
        for reg_key in reg_keys:
            product_name, product_key = self.getInformation(reg_key)
            self.sql.addValueToTable("keys", product_name, product_key)
    
    def log(self):
        self.logWindowsKey()
        self.logOfficeKeys()
