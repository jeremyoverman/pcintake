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
def getServices(self):
    """Get list of all services with their associated startmode."""
    
    command = "wmic service get Caption,StartMode /format:list"
    output = Popen(command, stdout=PIPE).stdout.readlines()
    
    services = {}
    current_service = None
    
    for line in output:
        line = line.strip()
        if len(line) > 0:
            key = line.split("=")[0]
            value = line.split("=")[1] 
            if  key == "Caption":
                services[value] = None
                current_service = value
            elif key == "StartMode":
                if value == "Auto": value = "Automatic" 
                services[current_service] = value
    
    return services
                
def logAbnormalServiceStartup(self, log):
    """Log any default services that do not have the default startmode."""
    
    services = self.getServices()
    
    log.addTitle("Abnormal Service Startmodes")
    
    log.addLine("(StartMode | Default) Service\n")
    
    for service in services:
        current_startmode = services[service]
        try:
            default_startmode = defaultservices.windows_7[service]
        except KeyError:
            pass
        else:
            if current_startmode != default_startmode:
                log.addLine("(%s | %s) %s" % (current_startmode, default_startmode, service))

def logNonDefaultServices(self, log):
    """Log all services that are not installed by default and their associated startmode."""
    
    log.addTitle("Non-default Services")
    
    services = self.getServices()
    
    for service in services:
        if service not in defaultservices.windows_7:
            log.addLine("(%s) %s" % (services[service], service))
            
    

windows_7 = {
"ActiveX Installer (AxInstSV)": "Manual",
"Adaptive Brightness": "Manual",
"Application Experience": "Manual",
"Application Identity": "Manual",
"Application Information": "Manual",
"Application Layer Gateway Service": "Manual",
"Application Management": "Manual",
"Background Intelligent Transfer Service": "Manual",
"Base Filtering Engine": "Automatic",
"Bitlocker Drive Encryption Service": "Manual",
"Block Level Backup Engine Service": "Manual",
"Bluetooth Support Services": "Manual",
"BranchCache": "Manual",
"Certificate Propagation": "Manual",
"CNG Key Isolation": "Manual",
"COM+ Event System": "Automatic",
"COM+ System Application": "Manual",
"Computer Browser": "Manual",
"Credential Manager": "Manual",
"Cryptographic Services": "Automatic",
"DCOM Server Process Launcher": "Automatic",
"Desktop Window Manager Session Manager": "Automatic",
"DHCP Client": "Automatic",
"Diagnostic Policy Service": "Automatic",
"Diagnostic Service host": "Automatic",
"Diagnostic System Host": "Manual",
"Disk Defragmenter": "Manual",
"Distributed Link Tracking Client": "Automatic",
"Distributed Transaction Coordinator": "Manual",
"DNS Client": "Automatic",
"Encrypting File System (EFS)": "Manual",
"Extensible Authentication Protocol": "Manual",
"Fax": "Manual",
"Function Discovery Provider Host": "Manual",
"Function Discovery Resource Publication": "Manual",
"Group Policy Client": "Automatic",
"Health Key and Certificate Management": "Manual",
"HomeGroup Listener": "Manual",
"HomeGroup Provider": "Manual",
"Human Interface Device Access": "Manual",
"IKE and AuthIP IPsec Keying Modules": "Manual",
"Interactive Services Detection": "Manual",
"Internet Connection Sharing (ICS)": "Disabled",
"IP Helper": "Automatic",
"IPsec Policy Agent": "Manual",
"KtmRm for Distributed Transaction Coordinator": "Manual",
"Link-Layer Topology Discovery Mapper": "Manual",
"Media Center Extender Service": "Disabled",
"Microsoft .NET Framework NGEN v2.0.50727_X86": "Manual",
"Microsoft iSCSI Initiator Service": "Manual",
"Microsoft Software Shadow Copy": "Manual",
"Multimedia Class Scheduler": "Automatic",
"Net.Tcp Port Sharing Service": "Disabled",
"Netlogon": "Manual",
"Network Access Protection Agent": "Manual",
"Network Connections": "Manual",
"Network List Service": "Manual",
"Network Location Awareness": "Automatic",
"Network Store Interface Service": "Automatic",
"Offline Files": "Automatic",
"Parental Controls": "Manual",
"Peer Name Resolution Protocol": "Manual",
"Peer Networking Grouping": "Manual",
"Peer Networking Identity Manager": "Manual",
"Performance Counter DLL Host": "Manual",
"Performance Logs & Alerts": "Manual",
"Plug and Play": "Automatic",
"PnP-X IP Bus Enumerator": "Manual",
"PNRP Machine Name Publication Service": "Manual",
"Portable Device Enumerator Service": "Manual",
"Power": "Automatic",
"Print Spooler": "Automatic",
"Problem Reports and Solutions Control Panel Support": "Manual",
"Program Compatibility Assistant Service": "Manual",
"Protected Storage": "Manual",
"Quality Windows Audio Video Experience": "Manual",
"Remote Access Auto Connection Manager": "Manual",
"Remote Access Connection Manager": "Manual",
"Remote Procedure Call (RPC)": "Automatic",
"Remote Procedure Call (RPC) Locator": "Manual",
"Remote Registry": "Manual",
"Routing and Remote Access": "Disabled",
"RPC Endpoint Mapper": "Automatic",
"Secondary Logon": "Manual",
"Secure Socket Tunneling Protocol Service": "Manual",
"Security Accounts Manager": "Automatic",
"Security Center": "Automatic",
"Server": "Automatic",
"Shell Hardware Detection": "Automatic",
"Smart Card": "Manual",
"Smart Card Removal Policy": "Manual",
"SNMP Trap": "Manual",
"Software Protection": "Automatic",
"SPP Notification Service": "Manual",
"SSDP Discovery": "Manual",
"Superfetch": "Automatic",
"System Event Notification Service": "Automatic",
"Tablet PC Input Service": "Automatic",
"Task Scheduler": "Automatic",
"TCP/IP NetBIOS Helper": "Automatic",
"Telephony": "Manual",
"Themes": "Automatic",
"Thread Ordering Server": "Manual",
"TP AutoConnect Service": "Manual",
"TPM Base Services": "Manual",
"UPnP Device Host": "Manual",
"User Profile Service": "Automatic",
"Virtual Disk": "Manual",
"Volume Shadow Copy": "Manual",
"WebClient": "Manual",
"Windows Audio": "Automatic",
"Windows Audio Endpoint Builder": "Automatic",
"Windows Backup": "Manual",
"Windows CardSpace": "Manual",
"Windows Color System": "Manual",
"Windows Connect Now - Config Registrar": "Manual",
"Windows Defender": "Automatic",
"Windows Driver Foundation - User-mode Driver Framework": "Automatic",
"Windows Error Reporting Service": "Manual",
"Windows Event Collector": "Manual",
"Windows Event Log": "Automatic",
"Windows Firewall": "Automatic",
"Windows Font Cache Service": "Manual",
"Windows Image Acquisition (WIA)": "Manual",
"Windows Installer": "Manual",
"Windows Management Instrumentation": "Automatic",
"Windows Media Center Receiver Service": "Manual",
"Windows Media Center Scheduler Service": "Manual",
"Windows Media Player Network Sharing Service": "Manual",
"Windows Modules Installer": "Manual",
"Windows Presentation Foundation Font Cache 3.0.0.0": "Manual",
"Windows Remote Management (WS-Management)": "Manual",
"Windows Search": "Automatic",
"Windows Time": "Automatic",
"Windows Update": "Automatic",
"WinHTTP Web Proxy Auto-Discovery Service": "Manual",
"Wired AutoConfig": "Manual",
"WLAN AutoConfig": "Manual",
"WMI Performance Adapter": "Manual",
"Workstation": "Automatic"            
}
windows_8 = {
"ActiveX Installer (AxInstSV)": "Manual",
"Application Experience": "Manual",
"Application Identity": "Manual",
"Application Information": "Manual",
"Application Layer Gateway Service": "Manual",
"Application Management": "Not Available",
"Background Intelligent Transfer Service": "Manual",
"Background Tasks Infrastructure Service": "Automatic",
"Base Filtering Engine": "Automatic",
"BitLocker Drive Encryption Service": "Manual",
"Block Level Backup Engine Service": "Manual",
"Bluetooth Support Service": "Manual",
"BranchCache": "Not Available",
"Certificate Propagation": "Manual",
"Client for NFS": "Not Available",
"CNG Key Isolation": "Manual",
"COM+ Event System": "Automatic",
"COM+ System Application": "Manual",
"Computer Browser": "Manual",
"Credential Manager": "Manual",
"Cryptographic Services": "Automatic",
"DCOM Server Process Launcher": "Automatic",
"Device Association Service": "Manual",
"Device Install Service": "Manual",
"Device Setup Manager": "Manual",
"DHCP Client": "Automatic",
"Diagnostic Policy Service": "Automatic",
"Diagnostic Service Host": "Manual",
"Diagnostic System Host": "Manual",
"Distributed Link Tracking Client": "Automatic",
"Distributed Transaction Coordinator": "Manual",
"DNS Client": "Automatic",
"Encrypting File System (EFS)": "Manual",
"Extensible Authentication Protocol": "Manual",
"Family Safety": "Manual",
"File History Service": "Manual",
"Function Discovery Provider Host": "Manual",
"Function Discovery Resource Publication": "Manual",
"Group Policy Client": "Automatic",
"Health Key and Certificate Management": "Manual",
"HomeGroup Listener": "Manual",
"HomeGroup Provider": "Manual",
"Human Interface Device Access": "Manual",
"Hyper-V Data Exchange Service": "Manual",
"Hyper-V Guest Shutdown Service": "Manual",
"Hyper-V Heartbeat Service": "Manual",
"Hyper-V Remote Desktop Virtualization Service": "Manual",
"Hyper-V Time Synchronization Service": "Manual",
"Hyper-V Volume Shadow Copy Requestor": "Manual",
"IKE and AuthIP IPsec Keying Modules": "Manual",
"Interactive Services Detection": "Manual",
"Internet Connection Sharing (ICS)": "Disabled",
"IP Helper": "Automatic",
"IPsec Policy Agent": "Manual",
"KtmRm for Distributed Transaction Coordinator": "Manual",
"Link-Layer Topology Discovery Mapper": "Manual",
"Local Session Manager": "Automatic",
"Microsoft Account Sign-in Assistant": "Manual",
"Microsoft iSCSI Initiator Service": "Manual",
"Microsoft Software Shadow Copy Provider": "Manual",
"Multimedia Class Scheduler": "Automatic",
"Netlogon": "Manual",
"Network Access Protection Agent": "Manual",
"Network Connected Devices Auto-Setup": "Manual",
"Network Connections": "Manual",
"Network Connectivity Assistant": "Manual",
"Network List Service": "Manual",
"Network Location Awareness": "Automatic",
"Network Store Interface Service": "Automatic",
"Offline Files": "Manual",
"Optimize Drives": "Manual",
"Peer Name Resolution Protocol": "Manual",
"Peer Networking Grouping": "Manual",
"Peer Networking Identity Manager": "Manual",
"Performance Logs & Alerts": "Manual",
"Plug and Play": "Manual",
"PNRP Machine Name Publication Service": "Manual",
"Portable Device Enumerator Service": "Manual",
"Power": "Automatic",
"Print Spooler": "Automatic",
"Printer Extensions and Notifications": "Manual",
"Problem Reports and Solutions Control Panel Support": "Manual",
"Program Compatibility Assistant Service": "Manual",
"Quality Windows Audio Video Experience": "Manual",
"Remote Access Auto Connection Manager": "Manual",
"Remote Access Connection Manager": "Manual",
"Remote Desktop Configuration": "Manual",
"Remote Desktop Services": "Manual)",
"Remote Desktop Services UserMode Port Redirector": "Manual",
"Remote Procedure Call (RPC)": "Automatic",
"Remote Procedure Call (RPC) Locator": "Manual",
"Remote Registry": "Disabled",
"Routing and Remote Access": "Disabled",
"RPC Endpoint Mapper": "Automatic",
"Secondary Logon": "Manual",
"Secure Socket Tunneling Protocol Service": "Manual",
"Security Accounts Manager": "Automatic",
"Security Center": "Automatic",
"Sensor Monitoring Service": "Manual",
"Server": "Automatic",
"Shell Hardware Detection": "Automatic",
"Smart Card": "Disabled",
"Smart Card Removal Policy": "Manual",
"SNMP Trap": "Manual",
"Software Protection": "Automatic",
"Spot Verifier": "Manual",
"SSDP Discovery": "Manual",
"Still Image Acquisition Events": "Manual",
"Storage Service": "Manual",
"Superfetch": "Automatic",
"System Event Notification Service": "Automatic",
"System Events Broker": "Manual",
"Task Scheduler": "Automatic",
"TCP/IP NetBIOS Helper": "Automatic",
"Telephony": "Manual",
"Themes": "Automatic",
"Thread Ordering Server": "Manual",
"Time Broker": "Manual",
"Touch Keyboard and Handwriting Panel Service": "Manual",
"UPnP Device Host": "Manual",
"User Profile Service": "Automatic",
"Virtual Disk": "Manual",
"Volume Shadow Copy": "Manual",
"WebClient": "Manual",
"Windows All User Install Agent": "Manual",
"Windows Audio": "Automatic",
"Windows Audio Endpoint Builder": "Automatic",
"Windows Backup": "Manual",
"Windows Biometric Service": "Manual",
"Windows Color System": "Manual",
"Windows Connect Now - Config Registrar": "Manual",
"Windows Connection Manager": "Automatic",
"Windows Defender Service": "Automatic",
"Windows Driver Foundation - User-mode Driver Framework": "Manual",
"Windows Error Reporting Service": "Manual",
"Windows Event Collector": "Manual",
"Windows Event Log": "Automatic",
"Windows Firewall": "Automatic",
"Windows Font Cache Service": "Automatic",
"Windows Image Acquisition (WIA)": "Manual",
"Windows Installer": "Manual",
"Windows Management Instrumentation": "Automatic",
"Windows Modules Installer": "Manual",
"Windows Remote Management (WS-Management)": "Manual",
"Windows Store Service (WSService)": "Manual",
"Windows Time": "Manual",
"Windows Update": "Manual",
"WinHTTP Web Proxy Auto-Discovery Service": "Manual",
"Wired AutoConfig": "Manual",
"WLAN AutoConfig": "Manual",
"WMI Performance Adapter": "Manual",
"Workstation": "Automatic",
"WWAN AutoConfig": "Manual"             
}