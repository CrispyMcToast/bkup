#!/usr/bin/python

import sys
import os
import hashlib
import time
import threading

import Guestimator
import Scanner

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
                update.append((key, value, "ADD"))
            if omap or omap[key] != value:
                update.append((key, value, "ADD"))
                omap.pop(key)

        for key,value in omap.iteritems():
            update.append((key,value,"RM")) 

        return update

    def print_status(self):
        scanned=int(self.scanner.get_total())
        total=int(self.guestimator.get_total())

        prct = 0
        if(total != 0 and scanned != 0):
            prct = float(scanned) / float(total)

        print("Scanned %d / Total %d | %f" % (scanned, total, prct))



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
            self.print_status()
            time.sleep(1)

        self.print_status()

        new_map = Scanner.get_hash()

        new_map = new_map.copy()
        old_map = self.bkup_map.copy()

        files = self.delta_check(old_map, new_map)
        
        print("Total files for update: %d" % len(files))

        start_len = len(files)
        threads = 0 
        workers = []
        while threads < MAX_THREADS and len(files) > 0
            w = OperationWorker()

        if not self.exit:
            self.complete = True
     
    def pause(self):
        self.runnable.clear()

    def unpause(self):
        self.runnable.set()

    def stop(self):
        self.exit = True
        self.runnable.clear()


sc = Bkup("/tmp/ColoradoTrip/", "blah")
sc.start()
