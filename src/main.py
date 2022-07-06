

import config  # 加载配置

import global_variable as glv
from input_process import inputParameters, isIceEnable
from terminal_command import mkdir,findTaskList
from DynamoRIO import DynamoRIO_Offline
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
    
    # get exe file list
    taskList = findTaskList()
    taskNum=0
    for exeTask in taskList:
        taskNum+=1
        passPrint("exeTask {:>3d}/{:>3d}: {}".format(taskNum,len(taskList),exeTask))
        DynamoRIO_Offline(exeTask)
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