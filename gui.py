import wx, threading
import wx.grid as grid
from wx.lib.stattext import GenStaticText 
import intake as Intake
import log

class Backend:
    def __init__(self):
        self.tables = []
    
    def runScans(self):
        if gui.services_panel.isClear():
            return
        self.sql = log.SQL()
        intake.initScanners()
        
        scan_index = gui.services_panel.list.GetChecked()
        intake.options["information"] = []
        for scan in scan_index:
            intake.options["information"].append(intake.scans[scan][1])
        
        i = 0
        for scan in intake.options["information"]:
            wx.CallAfter(gui.services_panel.selectService, scan_index[i])
            
            intake.iterateScanners(scan, self.sql)
            table, name, data = self.sql.tables[i]
            colnames = self.sql.getTableNames(table)
            self.tables.append([name, colnames, data])
            
            if intake.scanners[scan][1]:
                wx.CallAfter(gui.main_panel.results_notebook.addCustomResultsTab, scan, name, data, colnames)
            else:
                wx.CallAfter(gui.main_panel.results_notebook.addDefaultResultsTab, name, data, colnames)
            
            i += 1
            
        self.guiCleanup()
    
    def guiCleanup(self):
        wx.CallAfter(gui.services_panel.list.DeselectAll)
        wx.CallAfter(gui.services_panel.resetLabel)
        wx.CallAfter(gui.main_panel.customer_panel.button.Enable)
        wx.CallAfter(gui.setDefaultStatusText)
        wx.CallAfter(gui.enableSave)
        gui.services_panel.current_service = None
    
    def saveLog(self, output_file=None):
        logger = log.Log(self.sql)
        customer_name = gui.main_panel.customer_panel.getName()
        if not output_file:
            output_file = logger.writeLog(intake.options["output"], self.tables, customer_name)
        else:
            output_file = logger.writeLog(output_file, self.tables, customer_name)
        gui.SetStatusText("Log saved to %s." % output_file)
        
class ResultsGrid(wx.Panel):
    def __init__(self, parent, table, colnames):
        wx.Panel.__init__(self, parent)
        self.table = table
        self.colnames = colnames
        
        tab_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.grid = grid.Grid(self)
        
        tab_sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL)        
        
        self.createGrid()
        self.tidyGrid()
        
        self.grid.Bind(grid.EVT_GRID_CELL_RIGHT_CLICK, self.rightClickMenu)
        self.grid.Bind(grid.EVT_GRID_CELL_LEFT_DCLICK, self.selectCell)
        
        self.SetSizer(tab_sizer)
    
    def createGrid(self):
        cols = len(self.table[0])
        rows = len(self.table)
        
        self.grid.CreateGrid(rows, cols)
        
        row = 0
        
        for value in self.table:
            self.grid.SetCellValue(row, 0, value[0])
            if cols == 2:
                self.grid.SetCellValue(row, 1, value[1])
            row += 1
        
        i = 0
        for name in self.colnames:
            self.grid.SetColLabelValue(i, name)
            i += 1
    
    def tidyGrid(self):
        attr = grid.GridCellAttr()
        attr.SetReadOnly(True)
        self.grid.SetColAttr(0, attr)
        self.grid.SetColAttr(1, attr)
        self.grid.SetRowLabelSize(25)
        self.grid.AutoSize()
        self.grid.SetDefaultCellBackgroundColour("white")
        self.grid.SetLabelBackgroundColour("white")
        
    def selectCell(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.grid.ClearSelection()
        self.grid.SelectBlock(row, col, row, col)
    
    def rightClickMenu(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.grid.ClearSelection()
        self.grid.SelectBlock(row, col, row, col)
        text = self.grid.GetCellValue(row, col)
        
        menu = wx.Menu()
        copy_button = menu.Append(wx.ID_ANY, "&Copy", "Copy cells contents.")
        gui.Bind(wx.EVT_MENU, lambda x: self.copyCell(x, text), copy_button)
        
        gui.PopupMenu(menu, gui.ScreenToClient(wx.GetMousePosition()))
        
    def copyCell(self, event, text):
        clipdata = wx.TextDataObject()
        clipdata.SetText(text)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Flush()
        wx.TheClipboard.Close()
        
class ServicesList(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.current_service = None
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.CheckListBox(self)
        self.label = wx.StaticText(self, size=(100,20))
        
        self.sizer.Add(self.label, 0)
        self.sizer.Add(self.list, 1, wx.EXPAND | wx.VERTICAL)
        
        self.SetSizer(self.sizer)
        
        self.resetLabel()
        self.populateServicesList()
    
    def isClear(self):
        return len(self.list.GetChecked()) == 0
    
    def resetLabel(self):
        self.label.SetLabel("Select scans to run")
            
    def deselectServices(self, event):
        self.list.DeselectAll()
        if self.current_service != None:
            self.list.Select(self.current_service)
        
    def selectService(self, i):
        self.list.Select(i)
        self.current_service = i
    
    def populateServicesList(self):
        scans = intake.scans
        for scan in scans:
            index = self.list.Append(scan[0])
            if scan[1] in intake.options["information"]:
                self.list.Check(index)
    
    def tickAll(self, event=None):
        items = self.list.GetItems()
        for item in range(len(items)):
            self.list.Check(item)
        gui.changeRunState()
            
    def untickAll(self, event=None):
        items = self.list.GetItems()
        for item in range(len(items)):
            self.list.Check(item, False)
        gui.changeRunState()

class ResultsNotebook(wx.Notebook):
    def __init__(self, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)
        self.createDefaultPanel()
    
    def createDefaultPanel(self):
        self.default_panel = wx.Panel(self)
        self.default_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.default_label = GenStaticText(self.default_panel,
                                           label="Run scans to view results.",
                                           style=wx.ALIGN_CENTER)
        self.default_panel.SetSizer(self.default_sizer)
        self.default_sizer.Add(self.default_label, 1, wx.CENTER)
        
        self.default_label.BackgroundColour = "white"
        self.default_panel.Fit()
        self.AddPage(self.default_panel, "Scan Results")
        
    def addDefaultResultsTab(self, name, table, colnames):
        results_panel = ResultsGrid(self, table, colnames)
        self.AddPage(results_panel, name)
        
    def addCustomResultsTab(self, scan, name, table, colnames):
        scan_gui = intake.scanners[scan][1]
        results_panel = scan_gui(self, table, colnames)
        self.AddPage(results_panel, name)

class ResultsButtons(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_button = wx.Button(self, label="Save Results")
        self.save_button.Disable()
        
        self.sizer.Add(self.save_button)
        
        self.SetSizer(self.sizer)

class CustomerPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.label = wx.StaticText(self, label="Customer Name:", size=(100,18))
        self.textbox = wx.TextCtrl(self, size=(100,20))
        self.button = wx.Button(self, label="Run Scans", size=(80,22))
        
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTRE)
        self.sizer.Add(self.textbox, 1, wx.ALIGN_CENTRE)
        self.sizer.Add(self.button, 0, wx.ALIGN_CENTRE)
        
        self.SetSizer(self.sizer)

    def getName(self):
        return self.textbox.GetValue()

class MainPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.customer_panel = CustomerPanel(self)
        self.results_notebook = ResultsNotebook(self)
        self.results_buttons = ResultsButtons(self)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        #self.sizer.Add((20,20))
        self.sizer.Add(self.customer_panel, 0, wx.EXPAND)
        self.sizer.Add((20,20))
        self.sizer.Add(self.results_notebook, 1, wx.EXPAND)
        self.sizer.Add((10,10))
        self.sizer.Add(self.results_buttons, 0, wx.ALIGN_RIGHT)
        
        self.SetSizer(self.sizer)

class MenuBar(wx.MenuBar):
    def __init__(self, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        self.fileMenu()
        self.servicesMenu()
        self.helpMenu()
        self.disableSave()
        
    def fileMenu(self):
        self.file_menu = wx.Menu()
        self.file_save = self.file_menu.Append(wx.ID_SAVE,
                                     "&Save Results...\tCtrl + S",
                                     "Save the current results.")
        self.file_saveas = self.file_menu.Append(wx.ID_SAVEAS,
                                     "S&ave Results as...\tCtrl + Shift + S",
                                     "Save the current results as...")
        self.file_menu.AppendSeparator()
        self.file_exit = self.file_menu.Append(wx.ID_EXIT,
                                     "&Exit",
                                     "Exit this program.")
        self.Append(self.file_menu, "&File")
        
    def servicesMenu(self):
        self.services_menu = wx.Menu()
        self.services_select = self.services_menu.Append(wx.ID_ANY,
                                               "&Select All",
                                               "Select all services.")
        self.services_deselect = self.services_menu.Append(wx.ID_ANY,
                                                 "&Deselect All",
                                                 "Deselect all services.")
        self.Append(self.services_menu, "&Services")
        
    def helpMenu(self):
        self.help_menu = wx.Menu()
        self.help_about = self.help_menu.Append(wx.ID_ANY,
                                            "&About...",
                                            "About this program.")
        self.Append(self.help_menu, "&Help")
        
    def enableSave(self):
        self.Enable(self.file_save.GetId(), True)
        self.Enable(self.file_saveas.GetId(), True)
        
    def disableSave(self):
        self.Enable(self.file_save.GetId(), False)
        self.Enable(self.file_saveas.GetId(), False)

class GUI(wx.Frame):
    def __init__(self):
        
        wx.Frame.__init__(self, None, -1, 'PCIntake', size=(800,600))
        
        self.backend = None
        
        self.menu_bar = MenuBar()
        self.SetMenuBar(self.menu_bar)
        
        self.container_panel = wx.Panel(self)
        self.services_panel = ServicesList(self.container_panel)
        self.main_panel = MainPanel(self.container_panel)
        
        self.seperator = wx.StaticLine(self.container_panel, -1, style=wx.LI_VERTICAL)
        
        self.container_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.container_sizer.Add(self.services_panel, 0, wx.EXPAND | wx.ALL, 5)
        self.container_sizer.Add(self.seperator, 0, wx.EXPAND | wx.ALL, 5)
        self.container_sizer.Add(self.main_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.container_panel.SetSizer(self.container_sizer)
        
        self.CreateStatusBar()
        self.setDefaultStatusText()
                
        self.createBindings()
        self.createAccelerator()
        self.Layout()
        self.Show()

    def createBindings(self):
        self.main_panel.customer_panel.button.Bind(wx.EVT_BUTTON, self.runScans)
        self.services_panel.list.Bind(wx.EVT_LISTBOX, self.services_panel.deselectServices)
        self.main_panel.results_buttons.save_button.Bind(wx.EVT_BUTTON, self.saveLog)
        
        self.Bind(wx.EVT_MENU, self.exit, self.menu_bar.file_exit)
        self.Bind(wx.EVT_MENU, self.services_panel.tickAll, self.menu_bar.services_select)
        self.Bind(wx.EVT_MENU, self.services_panel.untickAll, self.menu_bar.services_deselect)
        self.Bind(wx.EVT_MENU, self.saveLog, self.menu_bar.file_save)
        self.Bind(wx.EVT_MENU, self.saveLogAs, self.menu_bar.file_saveas)
        self.Bind(wx.EVT_MENU, self.showAbout, self.menu_bar.help_about)
        
        self.Bind(wx.EVT_CHECKLISTBOX, self.changeRunState, self.services_panel.list)
    
    def createAccelerator(self):
        self.accel_table = wx.AcceleratorTable([
                                                (wx.ACCEL_CTRL, ord("S"),
                                                 self.menu_bar.file_save.GetId()
                                                 ),
                                                (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("S"),
                                                 self.menu_bar.file_saveas.GetId())
                                                ])
        
        self.SetAcceleratorTable(self.accel_table)
    
    def showAbout(self, event=None):
        info = wx.AboutDialogInfo()
        info.SetName("PC Intake")
        info.SetVersion(Intake.version)
        info.SetCopyright("(C) 2014 Jeremy Overman")
        info.SetDescription(Intake.description)
        info.SetWebSite("http://www.pcintake.com")
        wx.AboutBox(info)
    
    def setDefaultStatusText(self):
        self.SetStatusText("Choose the scans to run, enter the customer name then, then click Run Scan.")
    
    def enableSave(self):
        self.menu_bar.Enable(self.menu_bar.file_save.GetId(), True)
        self.menu_bar.Enable(self.menu_bar.file_saveas.GetId(), True)
        self.main_panel.results_buttons.save_button.Enable()
    
    def disableSave(self):
        self.menu_bar.Enable(self.menu_bar.file_save.GetId(), False)
        self.menu_bar.Enable(self.menu_bar.file_saveas.GetId(), False)
        self.main_panel.results_buttons.save_button.Disable()
    
    def saveLogAs(self, event=None):
        if self.backend:
            file_dialog = wx.FileDialog(self,
                                     "Save log to",
                                     "Logs",
                                     "",
                                     "Html File (*.html)|*.html",
                                      wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if file_dialog.ShowModal() != wx.ID_CANCEL:
                self.SetStatusText("Saving log...")
                output_file = file_dialog.GetPath()
                self.backend.saveLog(output_file)
    
    def saveLog(self, event=None):
        if self.backend:
            self.SetStatusText("Saving log...")
            self.backend.saveLog()
        
    def changeRunState(self, event=None):
        if self.services_panel.isClear():
            self.main_panel.customer_panel.button.Disable()
        else:
            self.main_panel.customer_panel.button.Enable()
    
    def exit(self, event):
        self.Close()
    
    def runScans(self, event=None):
        self.disableSave()
        self.services_panel.label.SetLabel("Running highlighted scan...")
        self.SetStatusText("Running scans...")
        self.main_panel.results_notebook.DeleteAllPages()
        self.main_panel.customer_panel.button.Disable()
        self.backend = Backend()
        self.thread = threading.Thread(target=self.backend.runScans)
        self.thread.start()

if __name__ == "__main__":
    app = wx.App()
    intake = Intake.Main()
    intake.initOptions()
    gui = GUI()
    app.MainLoop()