#!/usr/bin/env python

# Developed by MVelichko

import os
import sys
import time
import errno
import argparse
import subprocess
import SocketServer
from argparse import RawTextHelpFormatter
from multiprocessing import Manager, Pool, Process, cpu_count

manager = Manager()

flag = manager.dict()

def echo_server():
    HOST = "0.0.0.0"
    PORT = 12321

    class EchoServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
        pass

    class EchoRequestHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            print "connection from %s" % self.client_address[0]
            while True:
                line = self.rfile.readline()
                if not line:
                 break
                flag[line.rstrip()] = 0

            print "%s disconnected" % self.client_address[0]
    
    server = EchoServer((HOST, PORT), EchoRequestHandler)
    server.serve_forever()


def f(x):
    try:
        while True:
            if 'kill' in flag:
                print(" \nCpu consumption was remotely stopped.\nPlease use \'ctrl+c\' command to exit")
                break
            else:
                x ** x
                x = x + 99999
    except KeyboardInterrupt:
        pass # Just a stub for nicer output of KeyboardInterrupt exception


# CPU consumption tool doesn't work properly yet (need to make multicore CPU consumption stopping handle)
def cpu_eat(processes):
    try:
        print('Running load on CPU\nUtilizing %d core out of %d' % (processes, cpu_count()))
        processes_pool = []
        for i in range(processes):
            processes_pool.append(Process(target=f, args=(processes,)))
            processes_pool[i].start()
        p = Process(target=echo_server)
        p.start()
        p.join()
        processes_pool[i].join()
    except KeyboardInterrupt:
        print(" \nProgramm has been stopped")


def mem_eat():
    print("Memory consumption is started...\nPlease use \'ctrl+c\' command to exit.")
    a = []
    MEGA = 10 ** 6
    MEGA_STR = ' ' * MEGA
    try:
        while True:
            try:
                a.append(MEGA_STR)
            except MemoryError:
                time.sleep(60) # Adjust the time during which memory consumption will be at 100% constantly
                print("Programm has been stopped due to reaching memory limit")
                break
    except KeyboardInterrupt:
        print(" \nProgramm has been stopped")



# When consumption is started a file named 'eater' is created in current directory and started to growing. After catching 'KeyboardInterrupt' 'eater' will be deleted.
def disc_eat():
    write_str = "Full_space"*2048*2048*50  # Consume amount
    try:
        print("Discspace consumption is started...\nPlease use \'ctrl+c\' command to exit.")
        with open('eater', "w") as f:
            while True:
                try:
                    f.write(write_str)
                    f.flush()
                except IOError as err:
                    if err.errno == errno.ENOSPC:
                        write_str_len = len(write_str)
                        if write_str_len > 1:
                            write_str = write_str[:write_str_len/2]
                        else:
                            break
                        time.sleep(60)
                        os.remove('eater')
                        print("Discspace consumption has been stopped due to reaching disc space limit.\nRemoving 'eater' file...")
                    else:
                        raise
    except KeyboardInterrupt:
        os.remove('eater')
        print(" \nThe script has been stopped")
    except OSError:
        print(" \nThe script has been stopped")

parser = argparse.ArgumentParser(
        description="Universal script for testing CPU, RAM and discspace consumption. \nPlease choose required optional argument.",
        epilog="",formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("-c","--cpu", help="Consume all CPU. \nChoises are: \n    'a' - for all CPU cores consumption \n    'o' - for one CPU core consumption", choices=['a','o'])
parser.add_argument("-m","--memory", help="Consume all memory. \nMemory consumption will be at max level during 60s by default. It will cause freezes.", action="store_true")
parser.add_argument("-d","--disc", help="Consume all discspace by creating a file 'eater' in current directory. \nIt will be deleted automatically after the test.", action="store_true")
args = parser.parse_args()


if args.cpu == 'a':
    cpu_eat(cpu_count()) 
elif args.cpu == 'o':
    cpu_eat(1)
elif args.memory:
    mem_eat()
elif args.disc:
    disc_eat()

if len(sys.argv) == 1:
    parser.print_help()

