#!/usr/bin/python

import threading
import os
import hashlib
import time

MAX_THREADS = 5
thread_count = 0
tc_lock = threading.Lock()

def inc_count():
    global thread_count
    tc_lock.acquire()
    thread_count += 1
    tc_lock.release()

def dec_count():
    global thread_count
    tc_lock.acquire()
    thread_count -= 1
    tc_lock.release()

def get_count():
    global thread_count
    tc_lock.acquire()
    count = thread_count
    tc_lock.release()
    return count

hash_lock = threading.Lock()
scanned_hash = {}

def merge_hash(addative):
    hash_lock.acquire()
    scanned_hash.update(addative)
    hash_lock.release()

def get_hash():
    #TODO: is this ok?
    hash_lock.acquire()
    h = scanned_hash
    hash_lock.release()

    return h

class Scanner(threading.Thread):

    def __init__(self, base_path, master=True, appendable=""):
        threading.Thread.__init__(self)
        self.runnable = threading.Event()
        self.base_path = base_path
        self.total_processed = 0
        self.hashed_files = {}
        self.subthreads = []
        self.thread_lock = threading.Lock()
        self.appendable = appendable
        self.exit = False
        self.master = master

        self.complete = False

    def run(self):
        self.runnable.set()
        inc_count()

        self.scan()

        dec_count()

        while self.master and get_count() != 0:
            time.sleep(1)

        self.complete = True


    def finished(self):
        c = self.complete
        self.thread_lock.acquire()
        for s in self.subthreads:
            c = c & s.finished()
            print(s.finished())
        self.thread_lock.release()
        return c

    def get_total(self):
        return self.total_processed
            

    def scan(self):
        path = ""
        for root, subdir, files in os.walk(self.base_path):
            path = root

            self.total_processed += 1
            self.hashed_files[self.appendable+"/"] = 0

            while get_count() < MAX_THREADS and len(subdir) > 0:
                appended_path = self.appendable+"/"+subdir[0]

                s = Scanner(root+"/"+subdir[0], master=False,
                    appendable=appended_path)
                    
                self.thread_lock.acquire()
                self.subthreads.append(s)
                self.thread_lock.release()
                s.start()
                del subdir[0] 
             

            for f in files:
                try:
                    self.runnable.wait()
                    if self.exit:
                        return
                    fpath = path + "/" + f 
                    if not os.path.islink(fpath):
                        h = self.hash(fpath)
                        filep = self.remove_base(fpath)
                        self.total_processed += 1
                        self.hashed_files[self.appendable+"/"+filep] = h
                except PermissionError as e:
                    #ignore
                    continue
                except OSError as e:
                    #ignore
                    continue

            merge_hash(self.hashed_files)
            self.hashed_files={}

    def remove_base(self, path):
        return path[len(self.base_path)+1:]

    def hash(self, path, blocksize=65536):
        f = open(path, "rb")

        hasher = hashlib.sha256()

        buf = f.read(blocksize) 
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)

        return hasher.hexdigest()

    def pause(self):
        self.thread_lock.acquire()
        for s in self.subthreads:
            s.pause()
        self.thread_lock.release()
        self.runnable.clear()

    def unpause(self):
        self.thread_lock.acquire()
        for s in self.subthreads:
            s.unpause()
        self.thread_lock.release()
        self.runnable.set()

    def stop(self):
        self.thread_lock.acquire()
        for s in self.subthreads:
            s.stop()
        self.thread_lock.release()
        self.exit = True 
        self.runnable.clear()

