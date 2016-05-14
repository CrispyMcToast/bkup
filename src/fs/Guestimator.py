import threading 
import os
import time

class Guestimator(threading.Thread):

    def __init__(self, base_path):
        threading.Thread.__init__(self)
        self.base_path = base_path
        self.complete = False
        self.total_count = 0
        self.exit = False

        self.runnable = threading.Event()

        self.runnable.clear()

    def run(self):
        self.complete = False
        self.runnable.set()

        self.scan()

        if not self.exit:
            self.complete = True


    def scan(self):
        path = ""
        for root, subdir, files in os.walk(self.base_path):
            path = root
            self.total_count += 1
            for f in files:
                self.runnable.wait()
                if self.exit:
                    return
                fpath = path + "/" + f 
                if(os.access(fpath, os.R_OK)):
                    self.total_count += 1


    def finished(self):
        return self.complete

    def get_total(self):
        return self.total_count

    def pause(self):
        self.runnable.clear()

    def unpause(self):
        self.runnable.set()

    def stop(self):
        self.exit = True
        self.runnable.clear()

