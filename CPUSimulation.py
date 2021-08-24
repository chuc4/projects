import sys
import random
import math

alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

class Rand48(object):
    def srand48( self, seedval ):
        self.Xn = (seedval << 16) + 0x330E
    def drand48(self):
        self.Xn = (0x5DEECE66D * self.Xn + 0xB) & (2 ** 48 - 1)
        return self.Xn / (2 ** 48)

class Process(object):
    def __init__(self, arrivaltime, letter, tau_init):
        self.name = letter
        self.arrival = arrivaltime
        self.bursts = []
        self.taulast = tau_init #For printing, need to know last tau and current tau
        self.tau = tau_init
        self.waittime = []
        self.startwait = 0
        self.turnaroundtime = []
        self.burstleft = 0
        self.currentwait = 0
    def __lt__(self, other):
        if self.arrival == other.arrival:
            return self.name < other.name
        return self.arrival < other.arrival

def next_exp(rand48, lamb, bound):
    while (True):
        n = -(math.log(rand48.drand48())) / lamb
        if n < bound:
            return n

def generateProcesses(n, seed, lamb, bound):
    randseed = Rand48()
    randseed.srand48(seed)
    processes = []
    for i in range(n):
        arrivaltime = math.floor(next_exp(randseed, lamb, bound))
        p = Process(arrivaltime, alpha[i], 1/lamb)
        processes.append(p)

        numbursts = math.ceil(randseed.drand48()*100)

        for j in range(numbursts):
            bursttime = math.ceil(next_exp(randseed, lamb, bound))
            if (j != numbursts - 1):
                iotime = (math.ceil(next_exp(randseed, lamb, bound))) * 10
            else:
                iotime = None
            p.bursts.append((bursttime, iotime))
    processes.sort()
    return processes

def printProcesses(processes, lamb):
    alpha_processes = []
    init_tau = 1 / lamb
    for process in processes: 
        alpha_processes.append(process)
    alpha_processes.sort(key=lambda x: x.name)

    for p in alpha_processes:
        print("Process {} (arrival time {} ms) {} CPU bursts (tau {}ms)".format(p.name, p.arrival, len(p.bursts), int(init_tau)))

'''
command:
0 = begin sim
1 = process arrival
2 = CPU burst started
3 = CPU burst completed
4 = I/0 completed
5 = recalculating tau
6 = switching out of CPU/beginning I/0
7 = terminated process (finished)
8 = timeslice expired
else = end sim
'''

# prints the interesting events
# make sure process p is updated before running print!
# -->time is updated
# -->Q is updated (processes are added/removed before print is called)
# -->p.tau is calculated if needed

# argument types: (int, int (ms), array<Process>, Process, int, str)
def printWithTau(command, time, Q, p, cswitch, algo=None, preempt_p=None):
    if(time <= 999):
        if (command == 0):
            print("time %dms: Simulator started for %s" %(time, algo), end=" ")
        elif (command == 1):
            print("time %dms: Process %s (tau %dms) arrived; added to ready queue" %(time, p.name, p.tau), end=" ")
        elif (command == 2):
            print("time %dms: Process %s (tau %dms) started using the CPU for %dms burst" %(time, p.name, p.tau, p.bursts[0][0]), end=" ")
        elif (command == 3):
            if (len(p.bursts) > 2):
            #uses len(bursts) - 1 for num bursts to go, since the burst is complete but we still need the i/o time
                print("time %dms: Process %s (tau %dms) completed a CPU burst; %d bursts to go" %(time, p.name, p.tau, len(p.bursts) - 1), end=" ")
            else:
                print("time %dms: Process %s (tau %dms) completed a CPU burst; %d burst to go" %(time, p.name, p.tau, len(p.bursts) - 1), end=" ")
        elif (command == 4):
            print("time %dms: Process %s (tau %dms) completed I/O; added to ready queue" %(time, p.name, p.tau), end=" ")
        elif (command == 5):
            print("time %dms: Recalculated tau from %dms to %dms for process %s" %(time, p.taulast, p.tau, p.name), end=" ")
        elif (command == 6):
            print("time %dms: Process %s switching out of CPU; will block on I/O until time %dms" %(time, p.name, time + p.bursts[0][1] + cswitch/2), end=" ")
        elif (command == 7):
            print("time %dms: Process %s terminated" %(time, p.name), end=" ")
        elif (command == 8):
            print("time %dms: Process %s (tau %dms) completed I/O; preempting %s" %(time, p.name, p.tau, preempt_p.name), end=" ")
        elif (command == 9):
            print("time %dms: Process %s (tau %dms) started using the CPU for remaining %dms of %dms burst" %(time, p.name, p.tau, p.burstleft, p.bursts[0][0]), end=" ")
        elif (command == 10):
            print("time %dms: Process %s (tau %dms) will preempt %s" %(time, p.name, p.tau, preempt_p.name), end= " ")
        else:
            print("time %dms: Simulator ended for %s" %(time, algo), end=" ")
    else:
        if (command == 7):
            print("time %dms: Process %s terminated" %(time, p.name), end=" ")
        elif (command == 100):
            print("time %dms: Simulator ended for %s" %(time, algo), end=" ")
        else:
            return


    #Print [Q ...]
    if len(Q) == 0:
        print("[Q empty]")
        return
    print("[Q ", end = "")
    for process in Q:
        print("%s" %(process.name), end="")
    print("]")

def printNoTau(command, time, Q, p, cswitch, algo=None, tslice=None):
    if (time <= 999):
        if (command == 0):
            if algo == "RR":
                print("time %dms: Simulator started for %s with time slice %dms" %(time, algo, tslice), end=" ")
            else:
                print("time %dms: Simulator started for %s" %(time, algo), end=" ")
        elif (command == 1):
            print("time %dms: Process %s arrived; added to ready queue" %(time, p.name), end=" ")
        elif (command == 2):
            if (algo == "RR"):
                print("time %dms: Process %s started using the CPU for remaining %dms of %dms burst" %(time, p.name, p.burstleft, p.bursts[0][0]), end=" ")
            else:
                print("time %dms: Process %s started using the CPU for %dms burst" %(time, p.name, p.bursts[0][0]), end=" ")
        elif (command == 3):
            if (len(p.bursts) > 2):
            #uses len(bursts) - 1 for num bursts to go, since the burst is complete but we still need the i/o time
                print("time %dms: Process %s completed a CPU burst; %d bursts to go" %(time, p.name, len(p.bursts) - 1), end=" ")
            else:
                print("time %dms: Process %s completed a CPU burst; %d burst to go" %(time, p.name, len(p.bursts) - 1), end=" ")
        elif (command == 4):
            print("time %dms: Process %s completed I/O; added to ready queue" %(time, p.name), end=" ")
        elif (command == 5):
            print("time %dms: Recalculated tau from %dms to %dms for process %s" %(time, p.taulast, p.tau, p.name), end=" ")
        elif (command == 6):
            print("time %dms: Process %s switching out of CPU; will block on I/O until time %dms" %(time, p.name, time + p.bursts[0][1] + cswitch/2), end=" ")
        elif (command == 7):
            print("time %dms: Process %s terminated" %(time, p.name), end=" ")
        elif (command == 8):
            if (len(Q) == 0):
                print("time %dms: Time slice expired; no preemption because ready queue is empty" %time, end=" ")
            else: 
                print("time %dms: Time slice expired; process %s preempted with %dms to go" %(time, p.name, p.burstleft), end=" ")
        else:
            print("time %dms: Simulator ended for %s" %(time, algo), end=" ")
    else:
        if (command == 7):
            print("time %dms: Process %s terminated" %(time, p.name), end=" ")
        elif(command == 100):
            print("time %dms: Simulator ended for %s" %(time, algo), end=" ")
        else:
            return

    #Print [Q ...]
    if len(Q) == 0:
        print("[Q empty]")
        return
    print("[Q ", end = "")
    for process in Q:
        print("%s" %(process.name), end="")
    print("]")

def findTau(p, alpha):
    p.taulast = p.tau
    p.tau = math.ceil((alpha * p.bursts[0][0]) + ((1 - alpha) * p.taulast))

def findProcess(processes, name):
    for i in range(len(processes)):
        if processes[i].name == name:
            return i

def addIO(io, process, time, tcs):
    endtime = time + tcs/2 + process.bursts[0][1]
    if (len(io) == 0):
        io.append([endtime, process])
        return
    for i in range(len(io)):
        if io[i][0] == endtime:
            if (process.name < io[i][1].name):
                io.insert(i, [endtime, process])
                return
        elif io[i][0] > endtime:
            io.insert(i, [endtime, process])
            return
    io.append([endtime, process])
    return

def fcfs(cswitch, processes):
    switch_t = int(cswitch)/2 
    queue = []
    CPUBurst = []
    SwitchProcess = []
    currentIO = []
    waittimes = []
    tatimes = []
    time = 0
    numswitches = 0
    cputime = 0
    printNoTau(0, time, queue, None, cswitch, "FCFS")

    while(True):

        if len(processes) == 0:
            break

        #check if cpu burst has finished
        if len(CPUBurst) > 0:
            if CPUBurst[1] == 0:
                CPUBurst[0].turnaroundtime.append(time - CPUBurst[0].startwait + switch_t)
                if len(CPUBurst[0].bursts) - 1 <= 0:
                    waittimes.append(CPUBurst[0].waittime)
                    tatimes.append(CPUBurst[0].turnaroundtime)
                    printNoTau(7, time, queue, CPUBurst[0], cswitch, "FCFS")
                else: 
                    printNoTau(3, time, queue, CPUBurst[0], cswitch, "FCFS")
                    printNoTau(6, time, queue, CPUBurst[0], cswitch, "FCFS")
                numswitches += 1
                SwitchProcess.append(CPUBurst[0])
                SwitchProcess.append(switch_t)
                SwitchProcess.append("io")
                CPUBurst.clear()

        #check for process arrival
        for process in processes: 
            if process.arrival == time: 
                queue.append(process)
                printNoTau(1, time, queue, process, cswitch, "FCFS")
                process.startwait = time
        
        #check if nothing is running and something is in Q
        if len(queue) > 0 and len(SwitchProcess) == 0: 
            if len(SwitchProcess) == 0 and len(CPUBurst) == 0:
                queue[0].waittime.append(time - queue[0].startwait)
                SwitchProcess.append(queue[0])
                SwitchProcess.append(switch_t)
                SwitchProcess.append("cpu")
                queue.pop(0)

        #check if something is switching
        if len(SwitchProcess) > 0:
            if SwitchProcess[1] == 0:
                if SwitchProcess[2] == "cpu":
                    CPUBurst.append(SwitchProcess[0])
                    burst_time = SwitchProcess[0].bursts[0][0]
                    cputime += burst_time
                    CPUBurst.append(burst_time)
                    # queue.pop(0)
                    printNoTau(2, time, queue, SwitchProcess[0], cswitch, "FCFS")
                    SwitchProcess.clear()
                else: 
                    io_time = SwitchProcess[0].bursts[0][1]
                    if io_time == None:
                        index = findProcess(processes, SwitchProcess[0].name)
                        processes.pop(index)
                        SwitchProcess.clear()
                        continue
                    SwitchProcess[0].bursts.pop(0)
                    currentIO.append([SwitchProcess[0], io_time])
                    SwitchProcess.clear()

        newCurrentIO = []
        finishedIO = []
        #check if I/O is done
        for i in range(len(currentIO)):
            if currentIO[i][1] == 0:
                finishedIO.append(currentIO[i][0])
            else:
                newCurrentIO.append(currentIO[i])    
        currentIO = newCurrentIO   

        #print finished I/O and add to Q
        finishedIO.sort(key=lambda x: x.name)
        for j in range(len(finishedIO)):
            finishedIO[j].startwait = time
            queue.append(finishedIO[j])
            printNoTau(4, time, queue, finishedIO[j], cswitch, "FCFS")

        #if nothing is switching but there is something in Q
        if len(SwitchProcess) == 0: 
            if len(queue) > 0: 
                if len(SwitchProcess) == 0 and len(CPUBurst) == 0:
                    queue[0].waittime.append(time - queue[0].startwait)
                    SwitchProcess.append(queue[0])
                    SwitchProcess.append(switch_t)
                    SwitchProcess.append("cpu") 
                    queue.pop(0)

        if len(SwitchProcess) > 0:
            SwitchProcess[1] -= 1
        if len(CPUBurst) > 0: 
            CPUBurst[1] -= 1

        for io in currentIO:
            io[1] -= 1

        time += 1

    printNoTau(100, time, queue, None, cswitch, "FCFS")

    #calculate wait time
    total = 0
    num = 0
    for waitlist in waittimes:
        num += len(waitlist)
        for t in waitlist:
            total += t
    wait = total/num

    total = 0
    num = 0
    for talist in tatimes:
        num += len(talist)
        for t in talist:
            total += t
    turnaround = total/num
    cpu_util = (cputime/time)*100

    return wait, turnaround, numswitches, 0, cpu_util

def sjf_addtoQ(Q, process):
    if len(Q) == 0:
        Q.append((process))
        return
    for i in range(len(Q)):
        if Q[i].tau == process.tau:
            if (process.name < Q[i].name):
                Q.insert(i, process)
                return
        elif Q[i].tau > process.tau:
            Q.insert(i, process)
            return
    Q.append(process)

def sjf_arrival(processes, Q, time, timeleft, index, tcs):
    if (processes[index].arrival < timeleft + time):
        timeleft -= (processes[index].arrival - time)
        time = processes[index].arrival
        sjf_addtoQ(Q, processes[index])
        processes[index].startwait = time
        printWithTau(1, time, Q, processes[index], tcs)
        index += 1
    return time, timeleft, index

def sjf_iofinish(inIO, Q, time, timeleft, tcs):
    if (inIO[0][0] < timeleft + time):
        timeleft -= (inIO[0][0] - time)
        time = inIO[0][0]
        sjf_addtoQ(Q, inIO[0][1])
        inIO[0][1].startwait = time
        printWithTau(4, time, Q, inIO[0][1], tcs)
        inIO[0][1].bursts.pop(0)
        inIO.pop(0)
    return time, timeleft

def sjf_checkint(processes, Q, inIO, time, timeleft, index, tcs, Qempty):
    while (index < len(processes) and (processes[index].arrival < timeleft + time)) or (len(inIO) > 0 and (inIO[0][0] < timeleft + time)):
        if (Qempty and len(Q) > 0 and len(inIO) > 0 and inIO[0][0] > time and inIO[0][0] < tcs/2 + time):
            break
        if len(inIO) > 0 and index >= len(processes):
            time, timeleft = sjf_iofinish(inIO, Q, time, timeleft, tcs)
        elif len(inIO) == 0 and index < len(processes):
            time, timeleft, index = sjf_arrival(processes, Q, time, timeleft, index, tcs)
        else:
            if (inIO[0][0] < processes[index].arrival):
                time, timeleft = sjf_iofinish(inIO, Q, time, timeleft, tcs)
            else:
                time, timeleft, index = sjf_arrival(processes, Q, time, timeleft, index, tcs)
    time += timeleft
    return time, index

def sjf(processes, lamb, tcs, alpha):
    numswitches = 0
    cputime = 0
    TAtimes = []
    numpreempt = 0
    avgwait = []

    time = 0
    Q = []
    inIO = []
    popped = False

    printWithTau(0, time, Q, None, tcs, "SJF")
    index = 1
    time = processes[0].arrival
    sjf_addtoQ(Q, processes[0])
    processes[0].startwait = time
    printWithTau(1, time, Q, processes[0], tcs)
    while(len(processes) != 0):
        numswitches += 1
        
        #all blocking on I/O
        if (len(Q) == 0):
            Qempty = True
            timeleft = inIO[0][0] - time
            time, index = sjf_checkint(processes, Q, inIO, time, timeleft, index, tcs, Qempty)
        else:
            Qempty = False

        #Switch first item in Q to CPU
        timeleft = tcs/2
        if (len(inIO) > 0):
            if (inIO[0][0] - time < timeleft and inIO[0][0] - time > 0):
                if (len(Q) > 0):
                    inCPU = Q.pop(0)
                    popped = True

        time, index = sjf_checkint(processes, Q, inIO, time, timeleft, index, tcs, Qempty)
        if not popped:
            inCPU = Q.pop(0)
            popped = False
        if (inCPU == None and len(Q) > 0):
            inCPU = Q.pop(0)
        if (Qempty):
            timeleft = 0
            time, index = sjf_checkint(processes, Q, inIO, time, timeleft, index, tcs, Qempty)
        printWithTau(2, time, Q, inCPU, tcs)

        #check for arriving processes while CPU works
        #while there are processes arriving when CPU is working
        inCPU.waittime.append(time - inCPU.startwait - (tcs/2))
        timeleft = inCPU.bursts[0][0]
        cputime += timeleft
        time, index = sjf_checkint(processes, Q, inIO, time, timeleft, index, tcs, Qempty)
        
        #CPU burst completed
        if (len(inCPU.bursts) > 1):
            printWithTau(3, time, Q, inCPU, tcs)
            findTau(inCPU, alpha)
            printWithTau(5, time, Q, inCPU, tcs)

        #Switch out of CPU and in to I/O
        timeleft = tcs/2
        if (inCPU.bursts[0][1] != None):
            addIO(inIO, inCPU, time, tcs)
            printWithTau(6, time, Q, inCPU, tcs)
            inCPU.turnaroundtime.append(time - inCPU.startwait + tcs/2)
        else:
            inCPU.turnaroundtime.append(time - inCPU.startwait + tcs/2)

            printWithTau(7, time, Q, inCPU, tcs)
            processes.remove(inCPU)
            avgwait.append(inCPU.waittime)
            TAtimes.append(inCPU.turnaroundtime)

        inCPU = None
        time, index = sjf_checkint(processes, Q, inIO, time, timeleft, index, tcs, Qempty)
    printWithTau(100, time, Q, None, tcs, "SJF")

    #Calculate avg wait time
    total = 0
    num = 0
    for waitlist in avgwait:
        num += len(waitlist)
        for wait in waitlist:
            total += wait
    wait = total/num

    #Calculate avg turnaround
    total = 0
    num = 0
    for talist in TAtimes:
        num += len(talist)
        for ta in talist:
            total += ta
    avgturnaround = total/num

    cpu_util = (cputime/time)*100

    return wait, avgturnaround, numswitches, numpreempt, cpu_util

def srt_addPreemptedQueue(process, queue):
    if len(queue) == 0:
        queue.append(process)
        return
    
    added = False
    for q in range(len(queue)):
        time1 = process.tau - (process.bursts[0][0] - process.burstleft)
        time2 = queue[q].tau - (queue[q].bursts[0][0] - queue[q].burstleft)
        if process.burstleft == 0:
            time1 = process.tau
        if queue[q].burstleft == 0:
            time2 = queue[q].tau

        if time1 < time2: 
            queue.insert(q, process)
            added = True
            break
        elif time1 == time2:
            if process.name < queue[q].name:
                queue.insert(q, process) 
                added = True
                break
    if not added: 
        queue.append(process)

def srt_addQueue(process, queue):
    if len(queue) == 0:
        queue.append(process)
        return
    
    added = False
    for q in range(len(queue)):
        if process.tau < queue[q].tau: 
            queue.insert(q, process)
            added = True
            break
        elif process.tau == queue[q].tau:
            if process.name < queue[q].name:
                queue.insert(q, process) 
                added = True
                break
    if not added: 
        queue.append(process)

def srt_findPreempt(preempts, process):
    if preempts == None or len(preempts) == 0:
        return -1 
    for p in range(len(preempts)): 
        if process.name == preempts[p].name:
            return p
    return -1

def srt(cswitch, processes, alpha, lamb):
    switch_t = int(cswitch)/2 
    queue = []
    CPUBurst = []
    SwitchProcess = []
    currentIO = []
    preempted = []
    waittimes = []
    tatimes = []
    popQueue = False
    addedQueue = False
    prog_to_switch = None
    tau = 1 / lamb
    time = 0
    numswitches = 0
    preempts = 0
    cputime = 0

    printWithTau(0, time, queue, None, cswitch, "SRT")
    while(True): 
        madeIO = False

        if len(processes) == 0: 
            break 

        # if something is currently running
        if len(CPUBurst) > 0:
            if CPUBurst[1] == 0:
                CPUBurst[0].turnaroundtime.append(time - CPUBurst[0].start + switch_t) 
                CPUBurst[0].waittime.append(CPUBurst[0].currentwait)
                if len(CPUBurst[0].bursts) - 1 <= 0:
                    tatimes.append(CPUBurst[0].turnaroundtime)
                    waittimes.append(CPUBurst[0].waittime)
                    printWithTau(7, time, queue, CPUBurst[0], cswitch, "SRT")
                else:
                    printWithTau(3, time, queue, CPUBurst[0], cswitch, "SRT")
                    findTau(CPUBurst[0], alpha)
                    printWithTau(5, time, queue, CPUBurst[0], cswitch, "SRT")
                    printWithTau(6, time, queue, CPUBurst[0], cswitch, "SRT")
                SwitchProcess.append(CPUBurst[0])
                SwitchProcess.append(switch_t)
                SwitchProcess.append("io")
                CPUBurst.clear()
        
        #check for arrivals
        for process in processes: 
            if process.arrival == time: 
                process.tau = tau
                srt_addQueue(process, queue)
                process.start = time
                cputime += process.bursts[0][0]
                process.startwait = time
                process.currentwait = 0
                printWithTau(1, time, queue, process, cswitch, "SRT")

        #nothing is running and nothing is currently switching in
        if len(queue) > 0 and len(SwitchProcess) == 0: 
            if len(SwitchProcess) == 0 and len(CPUBurst) == 0: 
                SwitchProcess.append(queue[0])
                SwitchProcess.append(switch_t)
                SwitchProcess.append("cpu")
                queue.pop(0)
                poppedQueue = True
        
        #if something is done switching
        if len(SwitchProcess) > 0: 
            if SwitchProcess[1] == 0:
                index = srt_findPreempt(preempted, SwitchProcess[0])
                #process is switching into cpu
                if SwitchProcess[2] == "cpu":
                    numswitches += 1
                    SwitchProcess[0].currentwait += time - SwitchProcess[0].startwait - switch_t
                    if index != -1:
                        CPUBurst.append(SwitchProcess[0])
                        CPUBurst.append(SwitchProcess[0].burstleft)
                        time_passed = SwitchProcess[0].bursts[0][0] - SwitchProcess[0].burstleft
                        CPUBurst.append(SwitchProcess[0].tau - time_passed)
                        if(CPUBurst[0].bursts[0][0] == CPUBurst[1]):
                            printWithTau(2, time, queue, SwitchProcess[0], cswitch, "SRT")
                        else:
                            printWithTau(9, time, queue, SwitchProcess[0], cswitch, "SRT")
                        preempted[index].burstleft = 0
                        preempted.pop(index)
                    else:
                        CPUBurst.append(SwitchProcess[0])
                        burst_time = SwitchProcess[0].bursts[0][0]
                        CPUBurst.append(burst_time)
                        CPUBurst.append(SwitchProcess[0].tau)
                        printWithTau(2, time, queue, SwitchProcess[0], cswitch, "SRT")
                    
                    SwitchProcess.clear()
                #process is switching into io
                elif SwitchProcess[2] == "io": 
                    io_time = SwitchProcess[0].bursts[0][1]
                    if io_time == None:
                        index = findProcess(processes, SwitchProcess[0].name)
                        processes.pop(index)
                        SwitchProcess.clear()
                        continue
                    SwitchProcess[0].bursts.pop(0)
                    currentIO.append([SwitchProcess[0], io_time])
                    SwitchProcess.clear()
                #process was preempted
                else: 
                    preempts += 1
                    SwitchProcess.clear()
                    madeIO = True

                    newCurrentIO_t = []
                    finishedIO_t = []
                    for i in range(len(currentIO)):
                        if currentIO[i][1] == 0:
                            finishedIO_t.append(currentIO[i][0])
                        else:
                            newCurrentIO_t.append(currentIO[i])
                    currentIO = newCurrentIO_t

                    for j in range(len(finishedIO_t)):
                        time_passed = queue[0].bursts[0][0] - queue[0].burstleft
                        if len(CPUBurst) == 0 or finishedIO_t[j].tau < queue[0].tau - time_passed:
                            srt_addPreemptedQueue(finishedIO_t[j], queue)
                            finishedIO_t[j].startwait = time
                            addedQueue = True
                    
                    if len(queue) > 0:
                        if prog_to_switch != None:
                            SwitchProcess.append(queue[0])
                            SwitchProcess.append(switch_t)
                            SwitchProcess.append("cpu")
                            queue.pop(0)
                            queue.insert(0, prog_to_switch)
                            prog_to_switch.startwait = time
                            prog_to_switch = None
                        else:
                            SwitchProcess.append(queue[0])
                            SwitchProcess.append(switch_t)
                            SwitchProcess.append("cpu")
                            popQueue = True
                            srt_addPreemptedQueue(preempted[index], queue)

        if len(CPUBurst) > 0 and len(queue) > 0 and len(SwitchProcess) == 0:
             time_passed = CPUBurst[0].bursts[0][0] - CPUBurst[1]
             if queue[0].tau < CPUBurst[0].tau - time_passed:
                CPUBurst[0].burstleft = CPUBurst[1]
                preempted.append(CPUBurst[0])
                SwitchProcess.append(CPUBurst[0])
                SwitchProcess.append(switch_t)
                SwitchProcess.append("program")
                printWithTau(10, time, queue, queue[0], cswitch, "SRT", CPUBurst[0])
                prog_to_switch = CPUBurst[0]
                CPUBurst.clear()

        if not madeIO:
            newCurrentIO = []
            finishedIO = []
            for i in range(len(currentIO)):
                if currentIO[i][1] == 0:
                    finishedIO.append(currentIO[i][0])
                else:
                    newCurrentIO.append(currentIO[i])
            currentIO = newCurrentIO
        else:
            finishedIO = finishedIO_t

        for j in range(len(finishedIO)):
            cputime += finishedIO[j].bursts[0][0]
            if len(CPUBurst) > 0 and finishedIO[j].tau < CPUBurst[2]:
                queue.insert(0, finishedIO[j])
                finishedIO[j].startwait = time
                CPUBurst[0].burstleft = CPUBurst[1]
                preempted.append(CPUBurst[0])
                SwitchProcess.append(queue[0])
                SwitchProcess.append(switch_t)
                SwitchProcess.append("program")
                finishedIO[j].start = time
                finishedIO[j].currentwait = 0
                CPUBurst[0].startwait = time + switch_t
                printWithTau(8, time, queue, finishedIO[j], cswitch, "SRT", CPUBurst[0])
                CPUBurst.clear()
            else:
                if not madeIO:
                    srt_addPreemptedQueue(finishedIO[j], queue)
                    addedQueue = True
                finishedIO[j].start = time
                finishedIO[j].startwait = time
                finishedIO[j].currentwait = 0
                printWithTau(4, time, queue, finishedIO[j], cswitch, "SRT")

        if popQueue and not addedQueue:
            queue.pop(0)
            popQueue = False
        else:
            addedQueue = False

        if len(SwitchProcess) == 0: 
            if len(queue) > 0: 
                if len(SwitchProcess) == 0 and len(CPUBurst) == 0:
                    SwitchProcess.append(queue[0])
                    SwitchProcess.append(switch_t)
                    SwitchProcess.append("cpu") 
                    queue.pop(0)

        if len(SwitchProcess) > 0:
            SwitchProcess[1] -= 1
        if len(CPUBurst) > 0: 
            CPUBurst[1] -= 1
            CPUBurst[2] -= 1

        for io in currentIO:
            io[1] -= 1

        time += 1

    printWithTau(100, time, queue, None, cswitch, "SRT")

    total = 0
    num = 0
    for waitlist in waittimes:
        num += len(waitlist)
        for t in waitlist:
            total += t
    wait = total/num

    total = 0
    num = 0
    for talist in tatimes:
        num += len(talist)
        for t in talist:
            total += t
    turnaround = total/num
    cpu_util = (cputime/time)*100

    return wait, turnaround, numswitches, preempts, cpu_util


def rr(processes, lamb, tcs, tslice):
    time = 0
    Q = []
    inIO = []
    waittimes = []
    tatimes = []
    switchingin = None
    switchingout = None
    numswitches = 0
    preempts = 0
    cputime = 0
    index = 0
    incpu = None
    printNoTau(0, time, Q, None, tcs, "RR", tslice)
    endslice = None

    while(len(processes) != 0 or switchingout != None):
        #subtract 1ms from burst time
        if (incpu != None and switchingin == None):
            if (switchingout == None):
                incpu.burstleft -= 1

        #check if anything is done switching in
        if switchingin != None:
            switchingin = (switchingin[0] - 1, switchingin[1])
            if switchingin[0] == 0:
                switchingin = None
                if (incpu.burstleft == incpu.bursts[0][0]):
                    printNoTau(2, time, Q, incpu, tcs)
                else:
                    printNoTau(2, time, Q, incpu, tcs, "RR")
                endslice = time + tslice

        #check if anything is done switching out
        if switchingout != None:
            switchingout = (switchingout[0] - 1, switchingout[1])
            if (switchingout[0] == 0):
                if (len(Q) > 0):
                    incpu = Q[0]
                    incpu.currentwait += time - incpu.startwait
                    switchingin = (2, incpu)
                else:
                    incpu = None
                if (switchingout[1].burstleft > 0):
                    switchingout[1].startwait = time
                    Q.append(switchingout[1])
                elif (switchingout[1].burstleft == 0 and switchingout[1].bursts[0][1] != None):
                    addIO(inIO, switchingout[1], time - tcs/2, tcs)
                    switchingout[1].bursts.pop(0)
                switchingout = None

        #cpu burst finished
        if (incpu != None):
            if (incpu.burstleft == 0 and switchingout == None):
                incpu.waittime.append(incpu.currentwait)
                incpu.currentwait = 0
                incpu.turnaroundtime.append(time - incpu.start + tcs/2)
                numswitches += 1
                cputime += incpu.bursts[0][0]
                switchingout = (2, incpu)
                if (incpu.bursts[0][1] != None):
                    printNoTau(3, time, Q, incpu, tcs)
                    printNoTau(6, time, Q, incpu, tcs)
                else:
                    printNoTau(7, time, Q, incpu, tcs)
                    waittimes.append(incpu.waittime)
                    tatimes.append(incpu.turnaroundtime)
                    processes.remove(incpu)
        
        #timeslice ended, check for preemptions
        if (incpu != None) and (time == endslice) and (switchingout == None) and (switchingin == None):
            printNoTau(8, time, Q, incpu, tcs)
            if len(Q) > 0:
                numswitches += 1
                preempts += 1
                switchingout = (2, incpu)
            else:
                endslice = time + tslice

        #check if I/O has finished
        while (len(inIO) > 0 and inIO[0][0] == time):
            inIO[0][1].startwait = time
            inIO[0][1].start = time
            Q.append(inIO[0][1])
            inIO[0][1].burstleft = inIO[0][1].bursts[0][0]
            printNoTau(4, time, Q, inIO[0][1], tcs)
            inIO.pop(0)

        if (len(Q) > 0 and Q[0] == incpu):
            Q.pop(0)

        #check for arriving processes
        while (index < len(processes) and processes[index].arrival == time):
            Q.append(processes[index])
            printNoTau(1, time, Q, Q[-1], tcs)
            processes[index].startwait = time
            processes[index].start = time
            processes[index].currentwait = 0
            processes[index].burstleft = processes[index].bursts[0][0]
            index += 1
        
        #Nothing is currently running
        if (incpu == None and len(Q) > 0 and switchingin == None and switchingout == None):
            incpu = Q.pop(0)
            incpu.currentwait += time - incpu.startwait
            switchingin = (2, incpu)
        time += 1
    printNoTau(100, time - 1, Q, None, tcs, "RR")

    total = 0
    num = 0
    for waitlist in waittimes:
        num += len(waitlist)
        for t in waitlist:
            total += t
    wait = total/num

    total = 0
    num = 0
    for talist in tatimes:
        num += len(talist)
        for t in talist:
            total += t
    turnaround = total/num
    cpu_util = (cputime/(time-1))*100

    return wait, turnaround, numswitches, preempts, cpu_util

#argument types:(file, str, str, float, float, int, int, float)
def writetofile(f, algo, burst, wait, ta, cs, preempt, util):
    wait = "{:.3f}".format(wait)
    ta = "{:.3f}".format(ta)
    cs = str(cs)
    preempt = str(preempt)
    util = "{:.3f}".format(util)

    f.write("Algorithm " + algo + "\n")
    f.write("--average CPU burst time: " + burst + "\n")
    f.write("--average wait time: " + wait + "\n")
    f.write("--average turnaround time: " + ta + "\n")
    f.write("--total number of context switches: " + cs + "\n")
    f.write("--total number of preemptions: " + preempt + "\n")
    f.write("--CPU utilization: " + util + "%\n")
    return

def print_stderr(*a):
    print(*a, file = sys.stderr)

def checkerror(n, seed, l, bound, tcs, alpha, tslice):
    if n > 26 or n < 0:
        print_stderr("ERROR: number of processes must be positive and <= 26")
        quit()
    if (l >= 1 or l <= 0):
        print_stderr("ERROR: lambda must be < 1 and > 0")
        quit()
    if bound < 0:
        print_stderr("ERROR: bound must be a positive int")
        quit()
    if tcs % 2 != 0 or tcs <= 0:
        print_stderr("ERROR: context switch time must be a positive even integer")
        quit()
    if alpha < 0 or alpha >= 1:
        print_stderr("ERROR: alpha must be < 1 and >= 0")
        quit()
    if tslice < 1:
        print_stderr("ERROR: timeslice must be a positive integer")
        quit()

def check_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def main(argv):
    if len(argv) < 7:
        print_stderr("ERROR: Not enough arguments")
        quit()
    for i in [0, 1, 3, 4, 6]:
        if not (argv[i].isnumeric()):
            print_stderr("ERROR: invalid arguments")
            quit()
    for i in [2, 5]:
        if not (check_float(argv[2])):
            print_stderr("ERROR: invalid arguments")
            quit()
    n = int(argv[0])
    seed = int(argv[1])
    l = float(argv[2])
    bound = int(argv[3])
    tcs = int(argv[4])
    alpha = float(argv[5])
    tslice = int(argv[6])
    checkerror(n, seed, l, bound, tcs, alpha, tslice)

    f = open("simout.txt", 'w+')
    processes = generateProcesses(n, seed, l, bound)
    
    #Calculate burst time
    total = 0
    count = 0
    for p in processes:
        count += len(p.bursts)
        for b in p.bursts:
            total += b[0]
    avgburst = "{:.3f}".format(total/count)

    "Printing beginning"
    printProcesses(processes, l)
    print()
    
    "Here is the First Come First Serve Algorithm"
    wait, ta, cs, preempt, util = fcfs(tcs, processes)
    writetofile(f, "FCFS", avgburst, wait, ta, cs, preempt, util)
    print()

    "Here is the Shortest Job First Algorithm"
    processes = generateProcesses(n, seed, l, bound)
    wait, ta, cs, preempt, util = sjf(processes, l, tcs, alpha)
    writetofile(f, "SJF", avgburst, wait, ta, cs, preempt, util)
    print()

    "Here is the Shortest Remaining Time Algorithm"
    processes = generateProcesses(n, seed, l, bound)
    wait, ta, cs, preempt, util = srt(tcs, processes, alpha, l)
    writetofile(f, "SRT", avgburst, wait, ta, cs, preempt, util)
    print()

    "Here is the Round Robin Algorithm"
    processes = generateProcesses(n, seed, l, bound)
    wait, ta, cs, preempt, util = rr(processes, l, tcs, tslice)
    writetofile(f, "RR", avgburst, wait, ta, cs, preempt, util)

    f.close()

if __name__ == "__main__":
    main(sys.argv[1:])
    