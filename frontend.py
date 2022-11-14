import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import tkinter.simpledialog as sd
import tkinter.messagebox as msg
import threading as th
import time
import os
import matplotlib.pyplot as plt
#import multiprocessing as mtp

from stopth import StoppableThread
import backend

WAIT_MIN=1
WAIT_MAX=60

DIGIT_SET=set("0123456789")

START_TIME=None

DTEMP=[]
TIMES=[]
COMMENTS=[]
LAST_TIME=0

def pltTarget(fig):
    fig.clf()
    fig.plot(TIMES,DTEMP)
    fig.pause(0.4)

pltTh=StoppableThread(pltTarget)

def trans(s):
    ans = ''
    minus = s[5]
    if minus == '1':
        ans += "1"
    elif minus == 'b':
        ans += "-"
    elif minus == 'c':
        ans += "-1"
    ans += s[7] + '.' + s[9] + s[11] + s[13]
    return ans

def recordLoop(portx,starttime,lst):
    """循环代码基于https://github.com/Benzoin96485/Combust修改"""
    s,endtime=backend.backendLoop(portx)
    try:
        T=float(trans(s))
    except:
        return
    else:
        diff=round(endtime - starttime, 2)
        TIMES.append(diff)
        DTEMP.append(T)
        COMMENTS.append("")
        lst.insert("end",f"{diff:.2f}\t{T:.3f}\t\n")

recordTh=StoppableThread(recordLoop)

def getWindow():
    global recordTh
    global pltTh
    global START_TIME
    root=tk.Tk()
    # 端口选择
    ports=tk.Frame(root)
    port_label=tk.Label(ports,text="COM串口")
    port_list=ttk.Combobox(ports,state='readonly')
    port_con=tk.Button(ports,text="连接",state="active")
    port_label.pack()
    port_list.pack()
    port_con.pack()
    ports.pack()
    # 数据记录
    record=tk.Frame(root)
    wait=tk.Frame(record)
    wait_label=tk.Label(wait,text="间隔时间")
    wait_time=tk.Spinbox(wait,from_=WAIT_MIN,to=WAIT_MAX,validate="key")
    wait_label.pack()
    wait_time.pack()
    wait.pack()
    start=tk.Button(record,text="开始记录",state="disabled")
    start.pack()
    record.pack()
    result=tk.Frame(root)
    result_list=tk.Text(result)
    result_hand=tk.Button(result,text="手动记录")
    result_csv=tk.Button(result,text="导出CSV")
    result_plt=tk.Button(result,text="开始绘图")
    result_list.pack()
    result_hand.pack()
    result_csv.pack()
    result_plt.pack()
    result.pack()

    # 方法

    # 按下“连接”按钮
    # 当连接时，禁用端口列表，以防止端口改变，禁用开始按钮
    # 当不连接时，激活端口列表，可以选择端口
    def onConButClick():
        if port_list.get()!='':
            st=port_list.state()
            if "disabled" in st:
                port_list.config(state='readonly')
                port_con.config(text="连接")
                start.config(state="disabled")
            else:
                port_list.config(state="disabled")
                port_con.config(text="断开")
                start.config(state="active")

    port_con.config(command=onConButClick)

    # 点击端口列表
    # 更新端口列表，以防断连
    def onPortListClick():
        backend.updateComPorts()
        port_list.config(values=tuple(backend.COMPORTS))
        if port_list['values']:
            port_list.current(0)
    port_list.config(postcommand=onPortListClick)

    # 时间更改
    # 验证只能输入WAIT_MIN和WAIT_MAX之间的数字
    # TODO

    # 点击开始按钮
    # 开始时，
    # 结束时，激活端口列表，可以选择端口
    def onStartButClick():
        global recordTh
        global START_TIME
        global TIMES,DTEMP,COMMENTS
        st=port_con['state']
        if "disabled" in st:
            port_con.config(state='active')
            start.config(text="开始记录")
            recordTh.stop()
        else:
            port_con.config(state='disabled')
            start.config(text="结束记录")
            TIMES=[]
            DTEMP=[]
            COMMENTS=[]
            port=port_list.get()
            result_list.delete('1.0',"end")
            recordTh=StoppableThread(recordLoop)
            recordTh.setTimeOut(float(wait_time.get()))
            starttime=time.time()
            recordTh.setArgs((port,starttime,result_list))
            recordTh.start()
            START_TIME=starttime
    
    start.config(command=onStartButClick)

    # 手动记录按钮
    # 点击手动记录按钮，增添记录
    def onHandClick():
        port=port_list.get()
        s,endtime=backend.backendLoop(port)
        index=len(TIMES)
        try:
            T=float(trans(s))
        except:
            return
        else:
            TIMES.insert(index,round(endtime - START_TIME, 2))
            DTEMP.insert(index,T)
            C=sd.askstring(title="输入注释",prompt="请输入注释")
            COMMENTS.insert(index,C)
            result_list.insert(f"{index+1}.0",f"{round(endtime - START_TIME, 2):.2f}\t{T:.3f}\t{C}\n")
    result_hand.config(command=onHandClick)

    # 导出CSV
    def onCSVButClick():
        file_path=fd.asksaveasfilename(title='导出CSV',defaultextension=".csv")
        with open(file_path,"w") as f:
            f.write("Time/s\tT/K\tComment\n")
            for t,T,C in zip(TIMES,DTEMP,COMMENTS):
                f.write(f"{t:.2f}\t{T}\t{C}\n")
        msg.showinfo(title="保存文件",message="导出成功！")
    
    result_csv.config(command=onCSVButClick)

    def onPltButClick():
        global pltTh
        if pltTh.stopped():
            port_con.config(state='disabled')
            result_plt.config(text="结束绘图")
            pltTh=StoppableThread(pltTarget)
            pltTh.setTimeOut(float(wait_time.get()))
            plt.ion()
            pltTh.setArgs((plt,))
            pltTh.start()
        else:
            result_plt.config(text="开始绘图")
            pltTh.stop()
            plt.ioff()
    
    result_plt.config(command=onPltButClick)

    return root

if __name__=="__main__":
    root=getWindow()
    root.mainloop()