import os
import signal
from datetime import datetime
import readline

def makealist():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')
    a = input("shell->            " + "["+ current_time + "]"+'\n')
    buffer = ""
    flagquote = 0
    backquote = 0
    list = []
    for i in range(len(a)):
        if(a[i] == '"' and flagquote == 0):
            flagquote = 1
            buffer= buffer+'"'
        elif (a[i] == '"' and flagquote == 1):
            flagquote = 0
            buffer = buffer + '"'
            list.append(buffer)
            buffer = ""
        elif (a[i] == "\\" and flagquote == 0):
            backquote = 1
            buffer = buffer + "\\"
        elif (a[i] == "/" and backquote == 1 and flagquote == 0):
            backquote = 0
            buffer = buffer + "/"
            list.append(buffer)
            buffer = ""
        elif((a[i]) == " " and flagquote == 0 and backquote == 0):
            list.append(buffer)
            buffer = ""
        else:
            buffer = buffer + a[i]
    list.append(buffer)
    return a,list

def psh_cd(path):
    try:
        os.chdir(os.path.abspath(path))
    except Exception:
        print("cd: no such file or directory: {}".format(path))


background = False
myBgList = []
myBgNameList = []
myBgStatusList = []
def execute(a, alist,isBackGround):
    newpid = os.fork()
    if (a[0]=="b" and a[1]=="g" and a[2] == " " and alist[1]!="stop" and alist[1]!="start" and alist[1]!="kill" and alist[1]!="list"):
        myBgList.append(newpid)
        myBgNameList.append(a)
        myBgStatusList.append("running")
    else:
        myBgList.append(newpid)
        myBgNameList.append(a)
        myBgStatusList.append("running")
    if (newpid < 0):
         print("forking child process failed")
    elif newpid == 0:
        if(a == "pwd"):
            print(os.getcwd())
        elif(a[0] == "c" and a[1] == "d"):
            os.chdir(a[3:])
            newPath = os.getcwd()
            print("Current working directory is:", newPath)
        elif(isBackGround):
            alist = alist[1:]
            os.execvp(alist[0], alist)
        else:
            os.execvp(alist[0], alist)
    elif(not isBackGround):
        os.waitpid(newpid,0)
        idindex = myBgList.index(newpid)
        del myBgList[idindex]
        del myBgNameList[idindex]
        del myBgStatusList[idindex]
    else:
        os.waitpid(newpid,os.WNOHANG)

def config():
    color = open("sainashrc.txt","r")
    background = color.readline()
    forground = color.readline()
    bcolor = background[13:-1]
    fcolor = forground[12:]
    if(bcolor == "black"):
        bcolorstr = "40"
    elif (bcolor == "red"):
        bcolorstr = "41"
    elif(bcolor == "green"):
        bcolorstr = "42"
    elif(bcolor == "yellow"):
        bcolorstr = "43"
    elif(bcolor == "blue"):
        bcolorstr = "44"
    elif(bcolor == "magenta"):
        bcolorstr = "45"
    elif(bcolor == "cyan"):
        bcolorstr = "46"
    elif(bcolor == "white"):
        bcolorstr = "47"
    else:
        bcolorstr = ""
    if(fcolor == "black"):
        fcolorstr = "30"
    elif (fcolor == "red"):
        fcolorstr = "31"
    elif(fcolor == "green"):
        fcolorstr = "32"
    elif(fcolor == "yellow"):
        fcolorstr = "33"
    elif(fcolor == "blue"):
        fcolorstr = "34"
    elif(fcolor == "magenta"):
        fcolorstr = "35"
    elif(fcolor == "cyan"):
        fcolorstr = "36"
    elif(fcolor == "white"):
        fcolorstr = "37"
    else:
        fcolorstr = ""
    if(bcolorstr == ""):
        colorstring = "\x1b["+fcolorstr+"m"
    elif(fcolorstr == ""):
        colorstring = "\x1b["+bcolorstr+"m"
    elif(bcolorstr != "" and fcolorstr != ""):
        colorstring = "\x1b[" +fcolorstr+";" +bcolorstr + "m"
    else:
        colorstring = ""
    if(colorstring != ""):
        print(colorstring)

def runCommand():
    config()
    while(1):
        a,alist = makealist()
        if (a == "help"):
            print("sainash: a simple shell written in Python")
        elif (a == "exit"):
            break
        elif(a == ""):
            continue
        elif (a == "bglist"):
            for i in range(len(myBgList)):
                print("[ " + str(i+1)+ " ]" + " : " + str(myBgNameList[i]) + " " + myBgStatusList[i] + " ")
        elif(alist[0] == "bgkill"):
            os.kill(myBgList[int(alist[1])-1],signal.SIGTERM)
            del myBgList[int(alist[1])-1]
            del myBgNameList[int(alist[1])-1]
            del myBgStatusList[int(alist[1])-1]
        elif(alist[0] == "bgstop"):
            os.kill(myBgList[int(alist[1])-1],signal.SIGSTOP)
            myBgStatusList[int(alist[1]) - 1] = "suspended"
        elif (alist[0] == "bgstart"):
            os.kill(myBgList[int(alist[1]) - 1], signal.SIGCONT)
            myBgStatusList[int(alist[1]) - 1] = "running"
        else:
            if(a[0]=="b" and a[1]=="g" and a[2] == " " and alist[1]!="stop" and alist[1]!="start" and alist[1]!="kill" and alist[1]!="list"):
                execute(a,alist,1)
            else:
                execute(a,alist,0)
    return

def mymain():
    try:
        runCommand()
    except Exception:
        print("commandNotFound")


mymain()