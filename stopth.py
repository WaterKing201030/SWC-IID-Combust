"""
code from https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread
and https://stackoverflow.com/questions/36173410/python-terminate-a-thread-when-it-is-sleeping
"""

import threading

class StoppableThread(threading.Thread):
    def __init__(self,target,args=(),timeout=15):
        super(StoppableThread,self).__init__()
        self._target=target
        self._timeout=timeout
        self._args=args
        self._stop=threading.Event()
    def setTimeOut(self,timeOut):
        self._timeout=timeOut
    def setArgs(self,args):
        self._args=args
    def run(self):
        while not self.stopped():
            if not self.stopped():
                self._target(*self._args)
            self._stop.wait(self._timeout)
    def stop(self):
        self._stop.set()
    def stopped(self):
        return self._stop.is_set()