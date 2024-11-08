# Reproduce book environment
import random
random.seed(1234)

import logging
from pprint import pprint
from sys import stdout as STDOUT

# Write all output to a temporary directory
import atexit
import gc
import io
import os
import tempfile

TEST_DIR = tempfile.TemporaryDirectory()
atexit.register(TEST_DIR.cleanup)

# Make sure Windows processes exit cleanly
OLD_CWD = os.getcwd()
atexit.register(lambda: os.chdir(OLD_CWD))
os.chdir(TEST_DIR.name)

def close_open_files():
    everything = gc.get_objects()
    for obj in everything:
        if isinstance(obj, io.IOBase):
            obj.close()

atexit.register(close_open_files)

# Example 1
def factorize(number):
    for i in range(1, number + 1):
        if number % i == 0:
            yield i

# Example 2
import time
numbers =  [2139079, 1214759, 1516637, 1852285]
start = time.time()
for number in numbers:
    list(factorize(number))
end = time.time()
delta = end - start
print(f'Took {delta:.3f} seconds')

# Example 3
from threading import Thread
class FactorizeThread(Thread):
    def __init__(self, number):
        super().__init__()
        self.number = number

    def run(self):
        self.factors = list(factorize(self.number))
    
# Example 4
start = time.time()
threads = []
for number in numbers:
    thread = FactorizeThread(number)
    thread.start()
    threads.append(thread)

# Example 5
for thread in threads:
    thread.join()
end = time.time()
delta = end - start
print(f'Took {delta:.3f} seconds') # スレッドを使うほうがPython場合遅い.

# Example 6
import select # OSに対して0.3秒のブロッキングを要求する低速システムコール
import socket

def slow_systemcall():
    select.select([socket.socket()], [], [], 0.3)

# Example 7
start = time.time()
for _ in range(5):
    slow_systemcall()
end = time.time()
delta = end - start
print(f'Took {delta:.3f} seconds')

# Example 8
start = time.time()

threads = []
for _ in range(5):
    thread = Thread(target=slow_systemcall)
    thread.start()
    threads.append(thread)

# Example 9
def compute_helicopter_location(index):
    pass

for i in range(5):
    compute_helicopter_location(i)

for thread in threads:
    thread.join()


end = time.time()
delta = end - start
print(f'Took {delta:.3f} seconds')
