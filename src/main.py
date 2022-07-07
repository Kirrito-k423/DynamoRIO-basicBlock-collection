

import config  # 加载配置

import global_variable as glv
from input_process import inputParameters, isIceEnable
from terminal_command import mkdir,findTaskList,checkDiskUsage
from DynamoRIO import DynamoRIO_Offline, findTraceList,DynamoRIO_AssemblyLog
from tsjPython.tsjCommonFunc import *
# from excel import *
# from data import dataDictInit
# from multiProcess import *

def main():
    ## icecream & input
    args=inputParameters()
    isIceEnable(args.debug)

    # check directory
    mkdir(glv._get("outputFilePath")+glv._get("taskName"))
    mkdir(glv._get("outputFilePath")+glv._get("taskName")+"RawAssembly")
    
    # get exe file list
    taskList = findTaskList()

    # generate offline trace directory
    taskNum=0
    for exeTask in taskList:
        taskNum+=1
        passPrint("exeTask {:>3d}/{:>3d}: {}".format(taskNum,len(taskList),exeTask))
        DynamoRIO_Offline(exeTask)
        if not checkDiskUsage():
            break
        traceList = findTraceList()
        exeTaskName =re.search( r'\/(\w*)$',exeTask).group(1)
        for traceEntry in traceList:
            if re.search( '^drmemtrace\.{}\.'.format(exeTaskName),traceEntry):
                colorPrint("trace find {}".format(traceEntry),"cyan")
                DynamoRIO_AssemblyLog(traceEntry)

    
    # traceList = findTraceList()
    # taskNum=0
    # for traceEntry in traceList:
    #     taskNum+=1
    #     passPrint("traceTask {:>3d}/{:>3d}: {}".format(taskNum,len(traceList),traceEntry))
    #     DynamoRIO_AssemblyLog(traceEntry)

    # isFirstSheet=1
    # taskList = glv._get("taskList")
    # for taskKey, taskName in taskList.items():
    #     # glv._set("filename",pasteFullFileName(taskKey))
    #     filename=pasteFullFileName(taskKey)
    #     ic(filename)
    #     dataDict = dataDictInit()

    #     dataDict = readPartFile(taskName,filename, dataDict)
    #     print("blockSize {} {}".format(len(dataDict.get("unique_revBiblock")),len(dataDict.get("frequencyRevBiBlock"))))
    #     [llvmerror,osacaerror] = add2Excel(wb,taskName,isFirstSheet,dataDict)
    #     excelGraphAdd(wb,taskName,llvmerror,osacaerror)
    #     isFirstSheet=0
    # excelGraphBuild(wb)
if __name__ == "__main__":
    main()