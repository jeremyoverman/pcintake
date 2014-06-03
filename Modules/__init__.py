from subprocess import Popen, PIPE

__all__ = ["Antivirus",
           "EnvironmentVariables",
           "FailedDrivers",
           "FailedServices",
           "GeneralInformation",
           "InstalledPrograms",
           "ProductKeys",
           "StartupPrograms",
           "WEI"]

def getSubprocess(command):
    proc = Popen(command, stdout=PIPE, stderr=None)
    output = [''.join([x for x in y if ord(x) < 128]) for y in proc.stdout.readlines()]
    return output