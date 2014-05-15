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

import sqlite3
from mako.template import Template

class SQL:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.text_factory = str
        self.cur = self.db.cursor()
        self.tables = []
        
    def executeSQL(self, sql, *params):
        #print sql
        return self.cur.execute(sql)
        
    def createSQLList(self, values):
        sql = "("
        for field in values:
            sql += "'%s', " % field
        sql = sql[:-2] + ")"
        
        return sql
    
    def createTable(self, table, title, *fields):
        fields_fixed = []
        for field in fields:
            fields_fixed.append(field + " TEXT")
        self.tables.append([table, title, None])
        sql_list = self.createSQLList(fields_fixed)
        sql = "CREATE TABLE %s %s" % (table, sql_list)
        
        self.executeSQL(sql)
        
    def addValueToTable(self, table, *values):
        sql_list = self.createSQLList(values)
        sql = "INSERT INTO %s VALUES %s" % (table, sql_list)
        
        self.executeSQL(sql)
    
    def getTable(self, table):
        result = self.executeSQL("SELECT * FROM %s" % table)
        return result.fetchall()
    
    def Commit(self):
        self.cur.commit()

class Log:
    def __init__(self, sql, template="standard"):
        self.sql = sql
        template_file = "templates/standard/standard.html"
        self.mytemplate = Template(filename=template_file)
        self.globals = {"customer_name": "Jeremy"}
        
    def getDatabase(self):
        self.tables = []
        for table in self.sql.tables:
            name, title, data = table
            data = self.sql.getTable(name)
            self.tables.append((title, data))
    
    def writeLog(self, output):
        self.getDatabase()
        
        output_file = open(output, 'w')
        
        baked = self.mytemplate.render(tables=self.tables)
        output_file.write(baked)
        output_file.close()
        
if __name__ == "__main__":
    sql = SQL()
    sql.createTable("scan1", "Scan 1", "field1", "field2", "field3")
    sql.createTable("scan2", "Scan 2", "field1", "field2", "field3")
    sql.addValueToTable("scan1",  "a", "b", "c")
    sql.addValueToTable("scan1", "e", "f", "g")
    print sql.getTable("scan1")