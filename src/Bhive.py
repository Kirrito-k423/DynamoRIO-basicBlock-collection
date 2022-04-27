from terminal_command import TIMEOUT_COMMAND
import sys
import global_variable as glv
import re

# def checkBHiveResultStable(password,input,showinput,trytime):
#     global BHiveCount
#     order=0 
#     if trytime==0:
#         order=order+1
#     elif trytime>5:
#         return -1
#     sys.stdout.flush()
#     command=BHivePath+' '+input
#     list=TIMEOUT_COMMAND(command)
    
#     if list is None or len(list)==0:
#         regexResult=None
#     else:
#         regexResult=re.search("Event num: ([0-9]*)",list[-1])
#         # if not regexResult:
#         #     regexResult=re.search("Event num: ([0-9]*)",list[-2])
#     if regexResult:
#         resultCycle=regexResult.group(1)
#         return resultCycle
#     else:
#         return checkBHiveResultStable(password,input,showinput,trytime+1)
        
def BHive(input,showinput,trytime):
    global BHiveCount
    order=0 
    if trytime==0:
        order=order+1
    elif trytime>5:
        # print("trytime {}/{} {}".format(order,num_file,input))
        # print("trytime {}/{} {}".format(order,num_file,showinput))
        # print("trytime > 5")
        return -1
    # print("before main {}/{} {}".format(order,num_file,input))
    # print("before main {}/{} {}".format(order,num_file,showinput))
    sys.stdout.flush()
    # begin_time=time.time()
    command=glv._get("BHivePath")+' '+input+" "+str(glv._get("BHiveCount"))
    list=TIMEOUT_COMMAND(command)
    ic(list)

    if list is None or len(list)==0:
        regexResult=None
    else:
        regexResult=re.search("Event num: ([0-9]*)",list[-1])
        # if not regexResult:
        #     regexResult=re.search("Event num: ([0-9]*)",list[-2])
    if regexResult:
        resultCycle=regexResult.group(1)
        return resultCycle
	#checkCycle=checkBHiveResultStable(password,input,showinput,0)
        #if arroundPercent(5,resultCycle,checkCycle):
        #    return resultCycle
        #else:
        #    return BHive(password,input,showinput,trytime+1)   
    else:
        return BHive(input,showinput,trytime+1)

def BHiveInput(block):
    input2word=""
    for i in range(int((len(block)+1)/9)):
        input2word+=" 0x"+block[i*9:i*9+2]+" 0x"+block[i*9+2:i*9+4]
        input2word+=" 0x"+block[i*9+4:i*9+6]+" 0x"+block[i*9+6:i*9+8]
    return input2word

def BHiveInputDel0xSpace(block):
    input2word=""
    for i in range(int((len(block)+1)/9)):
        input2word+=block[i*9:i*9+2]+block[i*9+2:i*9+4]
        input2word+=block[i*9+4:i*9+6]+block[i*9+6:i*9+8]
    return input2word

def BHiveInputDel0x(block):
    input2word=""
    for i in range(int((len(block)+1)/9)):
        input2word+=" "+block[i*9:i*9+2]+" "+block[i*9+2:i*9+4]
        input2word+=" "+block[i*9+4:i*9+6]+" "+block[i*9+6:i*9+8]
    return input2word

def BHiveInputDelimiter(block):
    Delimiter="x"
    input2word=""
    for i in range(int((len(block)+1)/9)):
        input2word+=Delimiter+block[i*9:i*9+2]+Delimiter+block[i*9+2:i*9+4]
        input2word+=Delimiter+block[i*9+4:i*9+6]+Delimiter+block[i*9+6:i*9+8]
    return input2word