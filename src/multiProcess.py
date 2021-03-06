import global_variable as glv
import multiprocessing as mp
from data import queueDictInit
from multiprocessing import Pipe
from multiBar import *
from collections import defaultdict
from Bhive import *
from llvm_mca import *
from OSACA import *
from collections import defaultdict

class Process(mp.Process):
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            # raise e  # You can still rise this exception if you need to

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

def paralleReadProcess(filename,sendPipe,rank, startFileLine,endFileLine, queueDict):
    # unique_revBiblock_Queue,frequencyRevBiBlock_Queue,OSACAmaxCyclesRevBiBlock_Queue,OSACACPCyclesRevBiBlock_Queue,OSACALCDCyclesRevBiBlock_Queue,BhiveCyclesRevBiBlock_Queue,accuracyMax_Queue,accuracyCP_Queue,llvmmcaCyclesRevBiBlock_Queue,accuracyLLVM_Queue):
    # print("MPI Process Start {:2d} {}~{}".format(rank,startFileLine,endFileLine))
    fread=open(filename, 'r')

    # subDataDict=dataDictInit()
    
    unique_revBiblock=set()
    frequencyRevBiBlock = defaultdict(int)
    llvmmcaCyclesRevBiBlock = defaultdict(int)
    # OSACAmaxCyclesRevBiBlock = defaultdict(int)
    # OSACACPCyclesRevBiBlock = defaultdict(int)
    # OSACALCDCyclesRevBiBlock =  defaultdict(int)
    BhiveCyclesRevBiBlock = defaultdict(int)
    accuracyLLVM = defaultdict(float)
    accuracyLLVM_MuliplyFrequency = defaultdict(float)
    # accuracyMax = defaultdict(float)
    # accuracyCP = defaultdict(float)
    # for line in tqdm(fread.readlines()[startFileLine:endFileLine],total=endFileLine-startFileLine,desc=str("{:2d}".format(rank))):
    i=1
    try:
        for line in fread.readlines()[startFileLine:endFileLine]:
            if i%5==0:
                sendPipe.send(i)
            i+=1

            block=re.search('^(.*),',line).group(1)
            num=re.search(',(.*)$',line).group(1)

            unique_revBiblock.add(block)
            frequencyRevBiBlock[block] = int(num)
            BhiveCyclesRevBiBlock[block] = BHive(BHiveInputDelimiter(block),BHiveInputDel0xSpace(block),0)
            llvmmcaCyclesRevBiBlock[block] = LLVM_mca(capstone(capstoneInput(block)))
            # OSACAInput=saveOSACAInput2File(capstoneList(capstoneInput(block)),rank)
            # OSACAmaxCyclesRevBiBlock[block] = OSACA(password,OSACAInput,"max")
            # OSACACPCyclesRevBiBlock[block] = OSACA(password,OSACAInput,"CP")
            # OSACALCDCyclesRevBiBlock[block] = OSACA(password,OSACAInput,"LCD")
            accuracyLLVM[block]= calculateAccuracyLLVM(BhiveCyclesRevBiBlock[block],llvmmcaCyclesRevBiBlock[block])
            accuracyLLVM_MuliplyFrequency[block]=accuracyLLVM[block]* frequencyRevBiBlock[block]
            # accuracyMax[block]= calculateAccuracyOSACA(BhiveCyclesRevBiBlock[block],OSACAmaxCyclesRevBiBlock[block],rank)
            # accuracyCP[block]= calculateAccuracyOSACA(BhiveCyclesRevBiBlock[block],OSACACPCyclesRevBiBlock[block],rank)
    except Exception as e:
        sendPipe.send(e)
        errorPrint("error = {}".format(e))
        raise TypeError("paralleReadProcess = {}".format(e))
    fread.close() 
    # print("1rank{}".format(rank))
    queueDict.get("unique_revBiblock").put(unique_revBiblock)
    queueDict.get("frequencyRevBiBlock").put(frequencyRevBiBlock)
    # print("2rank{}".format(rank))
    queueDict.get("llvmmcaCyclesRevBiBlock").put(llvmmcaCyclesRevBiBlock)
    # queueDict.get("OSACAmaxCyclesRevBiBlock").put(OSACAmaxCyclesRevBiBlock)
    # queueDict.get("OSACACPCyclesRevBiBlock").put(OSACACPCyclesRevBiBlock)
    # queueDict.get("OSACALCDCyclesRevBiBlock").put(OSACALCDCyclesRevBiBlock)
    queueDict.get("BhiveCyclesRevBiBlock").put(BhiveCyclesRevBiBlock)
    # print("3rank{}".format(rank))
    queueDict.get("accuracyLLVM").put(accuracyLLVM)
    queueDict.get("accuracyLLVM_MuliplyFrequency").put(accuracyLLVM_MuliplyFrequency)
    # accuracyMax_Queue.put(accuracyMax)
    # accuracyCP_Queue.put(accuracyCP)
    sendPipe.send(50000)
    sendPipe.close()
    # print("MPI Process end {:2d} {}~{}".format(rank,startFileLine,endFileLine))

def fileLineNum(filename):
    # filename=glv._get("filename")
    fread=open(filename, 'r')
    num_file = sum([1 for i in open(filename, "r")])
    glv._set("num_file",num_file)
    fread.close() 
    return num_file

def mergeQueue2dataDict(queueDict,dataDict):
    for key, value in dataDict.dataDict.items():
        # ic(key,type(value))
        if isinstance(value,set):
            # ic("set")
            dataDict.dataDict[key]=dataDict.dataDict[key].union(queueDict.dataDict[key].get())
        elif isinstance(value,defaultdict):
            # ic("defaultdict(int)")
            dataDict.dataDict[key].update(queueDict.dataDict[key].get())
    return dataDict
def readPartFile(taskName,filename, dataDict):
    # unique_revBiblock,frequencyRevBiBlock,OSACAmaxCyclesRevBiBlock,OSACACPCyclesRevBiBlock,OSACALCDCyclesRevBiBlock,BhiveCyclesRevBiBlock,accuracyMax,accuracyCP,llvmmcaCyclesRevBiBlock,accuracyLLVM):
    num_file=fileLineNum(filename)
    ProcessNum=glv._get("ProcessNum")

    queueDict = queueDictInit(dataDict)

    sendPipe=dict()
    receivePipe=dict()
    total=dict()

    pList=[]
    for i in range(ProcessNum):
        startFileLine=int(i*num_file/ProcessNum)
        endFileLine=int((i+1)*num_file/ProcessNum)
        receivePipe[i], sendPipe[i] = Pipe(False)
        total[i]=endFileLine-startFileLine
        pList.append(Process(target=paralleReadProcess, args=(filename,sendPipe[i],i,startFileLine,endFileLine,queueDict)))

    for p in pList:
        p.start()
    

    # https://stackoverflow.com/questions/19924104/python-multiprocessing-handling-child-errors-in-parent
    if glv._get("debug")=='no':
        stdscr = curses.initscr()
        multBar(taskName,ProcessNum,total,sendPipe,receivePipe,pList,stdscr)
    
    while queueDict.get("unique_revBiblock").qsize()<ProcessNum:
        print("QueueNum : {}".format(queueDict.get("unique_revBiblock").qsize()))
        sys.stdout.flush()
        time.sleep(5)

    # for p in pList:
    #     p.join() # ??????????????????
        
    # for i in tqdm(range(ProcessNum)):
    for i in range(ProcessNum):
        # print("MPISum rank : {}, blockNum : {},leftQueueNum : {}".format(i,len(unique_revBiblock),unique_revBiblock_Queue.qsize()))
        dataDict=mergeQueue2dataDict(queueDict,dataDict)
    return dataDict
    # print(unique_revBiblock)
    # print(frequencyRevBiBlock)
    # print(accuracyMax)
    # print(len(unique_revBiblock))
    # print(len(frequencyRevBiBlock))