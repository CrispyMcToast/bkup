import shutil
import os
import threading
    
COPY_CMD = "COPY_CMD"
REMOVE_CMD = "RM_CMD"

class OperationWorker(threading.Thread):
    
    def __init__(self, todoq, resultsq):
        threading.Thread.__init__(self)

        self.todoq = todoq
        self.resultsq = resultsq


    def run(self):
        while True:
            operation = self.todoq.get()
            src, dst, command= operation

            afile = False
            if os.path.isfile(src):
                afile = True

            directory = False
            if os.path.isdir(src):
                directory = True

            if afile:
                if command == COPY_CMD:
                    self.copy_file(src, dst, operation)
                elif self.command == RM_CMD:
                    self.delete_file(src, dst, operation)
                else:
                    print("TODO: Error")
            elif directory:
                if command == COPY_CMD:
                    self.make_directory(src, dst, operation)
                elif command == RM_CMD:
                    self.delete_directory(src, dst, operation)
                else:
                    print("TODO: Error")
            else:
                print("TODO: Error")

    def copy_file(self, src, dst, operation):
        if os.path.isfile(src):
            print("Copy File src %s dst %s" % (src, dst))
            #sheutil.copy(src,dst)
            self.resultsq.put(operation, True)


    def make_directory(self, src, dst, operation):
        if os.path.isdir(src):
            print("Create Dir src %s dst %s" % (src, dst))
            #os.mkdir(dst)
            self.resultsq.put(operation, True)
        

    def delete_directory(self, src, dst, operation):
        if os.path.isdir(src):
            print("Delete Dir src %s dst %s" % (src, dst))
            #os.remove(dst)
            self.resultsq.put(operation, True)

    def delete_file(self, src, dst, operation):
        if os.path.isfile(src):
            print("Delete File src %s dst %s" % (src, dst))
            #os.remove(dst)
            self.resultsq.put(operation, True)
        
