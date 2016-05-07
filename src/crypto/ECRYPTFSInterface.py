#!/usr/bin/python

import os
import subprocess
#from subprocess import STDOUT, run
import getpass
import sys

class CryptSetupException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ECRYPTFSInterface:
    FNEK_SIG_CMD="ecryptfs-add-passphrase --fnek"
    ECRYPT_SIMPLE_CMD="ecryptfs-simple"

    params= {
        "key":"passphrase",
        "ecryptfs_enable_filename_crypto":"y",
        "passphrase_passwd":"",
        "ecryptfs_cipher":"aes",
        "ecryptfs_key_bytes":"32",
        "ecryptfs_fnek_sig":"",
        "ecryptfs_passthrough":"n"
    }

    enc_dir = ""
    unenc_dir = ""
    config_path = ""

    active = False 

    def __init__(self, enc_dir, unenc_dir, config_path):
        if os.path.exists(enc_dir) and os.path.exists(unenc_dir) and \
            os.path.exists(config_path):
            self.enc_dir = enc_dir
            self.unenc_dir = unenc_dir
            self.config_path = config_path
        else:
            raise CryptSetupException("Incorrect setup")


    def open(self):
        passw = getpass.getpass("Enter encryption passphrase")

        command = "%s" % (self.FNEK_SIG_CMD)
        p1= subprocess.Popen(args=command.split(), stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, universal_newlines=True, shell=True)

        (stdout,stderr) = p1.communicate(passw)

        if "Inserted" not in stdout:
            raise CryptSetupException("Unable to setup FNEK")

        #todo make better
        tok1 = stdout[41:57]
        #tok2 = stdout[116:132]

        self.params['ecryptfs_fnek_sig'] = tok1
        self.params['passphrase_passwd'] = passw

        optionsline = "-o "
        for key,value in self.params.items():
            optionsline = optionsline + key + "=" + value +","

        optionsline=optionsline[:-1]


        command = "%s %s %s %s" % (self.ECRYPT_SIMPLE_CMD, optionsline, \
            self.enc_dir, self.unenc_dir)
        res = subprocess.run(command.split(), stdout=subprocess.PIPE,
            universal_newlines=True)

        stdout = res.stdout

        if "Mounting" not in stdout:
            raise CryptSetupException("Unable to mount")

        active = True
        print("Succesfully mounted")

    def close(self):
        command = "umount %s" % (self.unenc_dir)
        if subprocess.run(command.split()).returncode != 0:
            raise CryptSetupException("Unable to unmount")

        active = False

    def get_unecnrypted_dir(self):
        if active:
            return self.unenc_dir
        else:
            return ""
        
    def loadConfig(self):
        key="passphrase"
        ecryptfs_enable_filename_crypto="y"
        passphrase_passwd="test"
        ecryptfs_cipher="aes"
        ecryptfs_key_bytes="32"
        ecryptfs_fnek_sig="d395309aaad4de06"
        ecryptfs_passthrough="n"

