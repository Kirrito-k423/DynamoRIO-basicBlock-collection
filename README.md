# DynamoRIO basic-block collection

通过DynamoRIO收集各种应用的make test或者其他benchmark的basic-block结果(TB级别的汇编log文件)，通过筛选和去重整理出供BHive测试运行的基本块测试集。

## 流程

1. 先采集offline raw文件
2. 分析raw文件，产生log
	1. (原本的raw文件先解析成trace文件，会变大几倍倍。
	2. trace文件翻译产生汇编log很慢。17h+
3. 筛选和去重log，得到BHive所需文件

### 采集数据所需空间

1. 采样30s。大约产生50GB raw文件
2. raw文件解析变成230GB trace文件
3. 导出汇编log文件 300GB+？(没结束)
4. 汇编精简

## 安装
### 安装DynamoRIO

请参考 https://github.com/DynamoRIO/dynamorio
### python库
```
pip install -r requirements.txt
```

## 运行
### 运行前必须修改的选项
执行文件等信息在`./src/config.py`下

### 查看选项
```
> python3 ./src/main.py -h
You can change all parameters in config.py except enter some parameters

usage: main.py [-h] [-b BHIVECOUNT] [-p PROCESSNUM] [-t TIMEOUT] [-d {yes,no}]

please enter some parameters

optional arguments:
  -h, --help            show this help message and exit
  -b BHIVECOUNT, --BHiveCount BHIVECOUNT
                        BHive Count Num (maybe useless depends on bin/bhive use
  -p PROCESSNUM, --ProcessNum PROCESSNUM
                        multiple Process Numbers
  -t TIMEOUT, --timeout TIMEOUT
                        sub program interrupt time(eg. llvm-mca, bhive, OSACA. less time causes less useful output
  -d {yes,no}, --debug {yes,no}
                        is print debug informations
```
### 推荐运行
```
python3 ./src/main.py -b 500 -p 20 -d no
```
## features

1. base on armV7
2. compare OSACA, LLVM-mca, Bhive
3. multiProcess
4. result in excel file with graph
5. icecream for debug
	* 优雅打印对象：函数名，结构体
	* 打印行号和栈（没用输入时
	* 允许嵌套（会将输入传递到输出
	* 允许带颜色`ic.format(*args)`获得ic打印的文本
	* debug `ic.disable()`and `ic.enable()`
	* 允许统一前缀 `ic.configureOutput(prefix='Debug | ')`
	* 不用每个文件import
	```
	from icecream import install
	install()

	ic.configureOutput(prefix='Debug -> ', outputFunction=yellowPrint)
	```
## To do
### bugs（已经修复）

python的子程序实现有问题，运行中，会有僵尸进程遗留下来（多达20个，需要按照下面手动kill，这也是核数建议为总核数的1/3的原因

### check process create time
```
ps -eo pid,lstart,cmd |grep bhive
date
```
### kill all process by name
```
 sudo ps -ef | grep 'bhive-re' | grep -v grep | awk '{print $2}' | sudo xargs -r kill -9
```

### 以为的原因

subProcess.pool 返回程序状态的时候，除了运行和结束状态，还有休眠等其他状态。也就是程序在发射之后并不是直接进入运行状态的。判断程序是否超时不能通过判断是否运行，因为一开始while循环进不去
```
while process.poll() is None:
```
而应该是判断是否正常结束(208是BHive结束返回值，不同程序不同)
```
while process.poll() != 208:
```
### 继续分析
实际debug还是有
![](https://shaojiemike.oss-cn-hangzhou.aliyuncs.com/img/20220625173740.png)

在debug输出里没有这些pid

check了，输出的个数是符合的。

不懂了，我都没调用，这僵尸进程哪里来的？除非是BHive产生的

### 杀死进程组

![](https://shaojiemike.oss-cn-hangzhou.aliyuncs.com/img/20220625185611.png)

可能设定是timeout是20秒，但是htop程序运行了2分钟也没有kill。这是正常的，因为主程序挤占资源导致挂起了，导致无法及时判断和kill