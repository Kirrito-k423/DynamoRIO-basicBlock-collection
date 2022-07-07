
from terminal_command import TIMEOUT_COMMAND,TIMEOUT_severalCOMMAND,checkFileByRegex
from tsjPython.tsjCommonFunc import *
import global_variable as glv



def DynamoRIO_Offline(exeTask):
    if not checkIfExisted(exeTask):
        command=glv._get("DynamoRIO-drrun")+" -s "+str(2*glv._get("timeout"))+\
                " -t drcachesim -outdir "+glv._get("outputFilePath")+glv._get("taskName")+\
                "  -offline -- "+exeTask[:-1]
        yellowPrint(command)
        inputTaskList=TIMEOUT_severalCOMMAND(command,glv._get("timeout"))
        ic(inputTaskList)

def DynamoRIO_AssemblyLog(traceEntry):
    if not checkLogExisted(traceEntry):
        traceEntryName=re.search( r'^drmemtrace\.(\w*)\.',traceEntry).group(1)+".log"
        command=glv._get("DynamoRIO-drrun")+\
                " -t drcachesim -simulator_type view -indir "+\
                glv._get("outputFilePath")+glv._get("taskName")+"/"+traceEntry[:-1]+\
                " > "+glv._get("outputFilePath")+glv._get("taskName")+"RawAssembly"+\
                "/"+traceEntryName+" 2>&1"
        yellowPrint(command)
        inputTaskList=TIMEOUT_severalCOMMAND(command,10000*glv._get("timeout"))
        ic(inputTaskList)

def checkIfExisted(exeTask):
    exeTaskName =re.search( r'\/(\w*)$',exeTask).group(1)
    ic(exeTaskName)
    outputDir=glv._get("outputFilePath")+glv._get("taskName")
    return checkFileByRegex(exeTaskName,outputDir)

def checkLogExisted(traceEntry):
    traceEntryName=re.search( r'^drmemtrace\.(\w*)\.',traceEntry).group(1)+".log"
    ic(traceEntryName)
    outputDir=glv._get("outputFilePath")+glv._get("taskName")+"RawAssembly"
    return checkFileByRegex(traceEntryName,outputDir)

def findTraceList():
    command='ls '+glv._get("outputFilePath")+glv._get("taskName")
    TraceList=TIMEOUT_severalCOMMAND(command,glv._get("findTimeout"))
    ic(TraceList)
    return TraceList