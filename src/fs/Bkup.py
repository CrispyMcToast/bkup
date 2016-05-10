#!/usr/bin/python

import sys
import os
import hashlib
import time
import threading
import queue

import Guestimator
import Scanner
import OperationWorker

class BkupException(Exception):
    def __init__(self, value):
            self.value = value

    def __str__(self):
            return repr(self.value)



class Bkup(threading.Thread):
    BKUP_FILE=".bkup_config"
    MAX_THREADS=5

    base_path = ""
    bkup_map = {}

    run = False

    def __init__(self, base_path, dst_dir):
        threading.Thread.__init__(self)
        self.runnable = threading.Event()

        self.dst_dir = dst_dir

        if os.path.exists(base_path):
            self.base_path = base_path
            bkup_map_loc = base_path + "/" + self.BKUP_FILE
            if os.path.exists(bkup_map_loc):
                f = open(bkup_map_loc, "r").read()
                self.bkup_map = eval(f)
                f.close()
        else:
            raise BkupException("Bad base path")

        self.exit= False

        self.guestimator = Guestimator.Guestimator(base_path)
        self.scanner = Scanner.Scanner(base_path)

        
    #does not guarantee consistency of maps - make copies
    def delta_check(self, omap, nmap):
        update = []

        while len(nmap) > 0:
            (key, value) = nmap.popitem()
            if key not in omap:
                update.append((key, OperationWorker.COPY_CMD))
            elif omap[key] != value:
                update.append((key, OperationWorker.COPY_CMD))
                omap.pop(key)

        for key,value in omap.items():
            update.append((key,OperationWorker.RM_CMD)) 

        return update

    def print_status(self, doing, part, total):

        prct = 0
        if(total != 0 and part!= 0):
            prct = (float(part) / float(total) * 100)

        print("%s %d / %d | %f" % (doing, part, total, prct))



    def run(self):
        self.complete = False
        self.runnable.set()

        self.guestimator.start() 
        self.scanner.start()

        while self.guestimator.finished() == False or self.scanner.finished() \
            == False:
            self.runnable.wait()
            if self.exit:
                break
            self.print_status("Scanning", int(self.scanner.get_total()),
                int(self.guestimator.get_total()))
            time.sleep(1)

        self.print_status("Scanning", int(self.scanner.get_total()),
            int(self.guestimator.get_total()))

        new_map = Scanner.get_hash()

        new_map = new_map.copy()
        old_map = self.bkup_map.copy()

        updates = self.delta_check(old_map, new_map)
        
        print("Total files for update: %d" % len(updates))

        threads = 0 
        workers = []

        todoq = queue.Queue()
        resultsq = queue.Queue()

        while threads < self.MAX_THREADS:
            worker = OperationWorker.OperationWorker(todoq, resultsq)
            worker.start()
            workers.append(worker)
            threads += 1

        for update in updates:
            path, command = update

            src = self.base_path + path
            dst = self.dst_dir + path

            todoq.put((src, dst, command))


        total_jobs = len(updates)
        while resultsq.qsize() != total_jobs:
            self.print_status("Updating", resultsq.qsize(), len(updates))
            time.sleep(1)
    
        self.print_status("Updating", resultsq.qsize(), len(updates))

        print("Completed")

        if not self.exit:
            self.complete = True
     
    def pause(self):
        self.runnable.clear()

    def unpause(self):
        self.runnable.set()

    def stop(self):
        self.exit = True
        self.runnable.clear()


sc = Bkup("/tmp/ColoradoTrip/", "/tmp/a")
sc.start()
