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
def download(item):
    return item

def resize(item):
    return item

def upload(item):
    return item

# Example 2
from collections import deque
from threading import Lock

class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()

# Example 3
    def put(self, item):
        with self.lock:
            self.items.append(item)
    
# Example 4
    def get(self):
        with self.lock:
            return self.items.popleft()
        
# Example 5
from threading import Thread
import time

class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0

# Example 6
    def run(self):
        while True:
            self.polled_count += 1
            try:
                item = self.in_queue.get()
            except IndexError:
                time.sleep(0.01) # 仕事がない(サボりだがCPUリソースを食う)
            except AttributeError:
                # The magic exit signal
                return 
            else:
                # 仕事をする
                result = self.func(item)
                self.out_queue.put(result)
                self.work_done += 1

# Example 7
download_queue = MyQueue()
resize_queue = MyQueue()
upload_queue = MyQueue()
done_queue = MyQueue()
threads = [
    Worker(download, download_queue, resize_queue),
    Worker(resize, resize_queue, upload_queue),
    Worker(upload, upload_queue, done_queue),
]

# Example 8
for thread in threads:
    thread.start()

for _ in range(1000):
    download_queue.put(object())

# Example 9
while len(done_queue.items) < 1000:
    # busy waiting: do something useful while waiting
    time.sleep(0.1)

# Stop all the threads by causing an exception in their run methods
for thread in threads:
    thread.in_queue = None
    thread.join()

# Example 10
processed = len(done_queue.items)
polled = sum(t.polled_count for t in threads)
print(f'Processed {processed} items after '
      f'polling {polled} times')


'''Queueを使うと前段と後段の作業者の速度差を調整しながらデータを転送できる
'''
# from queue import Queueは, 下記課題をすべて解決するモジュール
# 1. 前段と後段の作業者の速度さによって後段の作業者が暇を潰してCPUリソースを食う
# 2. すべての入力作業を完了したあとに完了チェックのためのビジーウェイトがある
# 3. 作業者(Worker)のrunメソッドは, 無限ループしている, 抜け出すためのシグナルがない
# 4. キューサイズが無限設定の場合だと、キューを食いつぶして、どこかでソフトがクラッシュする

# Example 11
from queue import Queue
my_queue = Queue()

def consumer():
    print("Consumer waiting")
    my_queue.get() # put()の後で実行
    print("Consumer done")

thread = Thread(target=consumer)
thread.start()

# Example 12
print("Producer putting")
my_queue.put(object()) # get()の前に実行
print("Producer done")
thread.join()

print("Waiting consumer -----")

# Example 13
# キューを消費する前に、しばらく待つスレッド
my_queue = Queue(1)
def consumer_at_moment_wait():
    time.sleep(0.1) # wait
    my_queue.get() # run
    print("Consumer got 1")
    my_queue.get() # run
    print("Consumer got 2")
    print("Consumer done")

thread = Thread(target=consumer_at_moment_wait)
thread.start()

# Example 14
my_queue.put(object())
print('Producer put 1')
my_queue.put(object())          # Runs third
print('Producer put 2')
print('Producer done')
thread.join()


print("Notification puroducer/consumer -----")

# Example 15
in_queue = Queue()

# 一つの作業を終えるとtask_doneでproducerに通知する
def consumer_notification():
    print('Consumer waiting')
    work = in_queue.get() # 2
    print('Consumer working')
    # do work
    print('Consumer done')
    in_queue.task_done() # 3 (task_done()で入力キューが減ってくるまで待機できる)

thread = Thread(target=consumer_notification)
thread.start()

# Example 16
print("Producer putting")
in_queue.put(object()) # 1
print("Producer waiting") # 4
in_queue.join() # in_queueは, キューに入れられたすべてのデータについてtask_doneが呼ばれるまでは, joinできないようになっている
print("Producer done")
thread.join()

print("Cooperative worker queue system -----")

# Example 17
class ClosableQueue(Queue):
    SENTINEL = object()
    
    def close(self):
        self.put(self.SENTINEL)
    
# Example 18
    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return
                yield item
            finally:
                self.task_done()

# Example 19
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        
    def run(self):
        for item in self.in_queue: # ClosableQueue.__iter__
            result = self.func(item)
            self.out_queue.put(result)
    
# Example 20
download_queue = ClosableQueue()
resize_queue = ClosableQueue()
upload_queue = ClosableQueue()
done_queue = ClosableQueue()
threads = [
    StoppableWorker(download, download_queue, resize_queue),
    StoppableWorker(resize, resize_queue, upload_queue),
    StoppableWorker(upload, upload_queue, done_queue),
]

# Example 21
for thread in threads:
    thread.start()

for _ in range(1000):
    download_queue.put(object())

download_queue.close()

# Example 22
download_queue.join()
resize_queue.close()
resize_queue.join()
upload_queue.close()
upload_queue.join()
print(done_queue.qsize(), 'items finished')

for thread in threads:
    thread.join()

print("Concurrent Workers in Cooperative queue system -----")

# Example 23
def start_threads(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads

def stop_threads(closable_queue, threads):
    for _ in threads:
        closable_queue.close()
        
    closable_queue.join()
    
    for thread in threads:
        thread.join()
        
# Example 24
download_queue = ClosableQueue()
resize_queue = ClosableQueue()
upload_queue = ClosableQueue()
done_queue = ClosableQueue()

download_threads = start_threads(3, download, download_queue, resize_queue)
resize_threads = start_threads(4, resize, resize_queue, upload_queue)
upload_threads = start_threads(5, upload, upload_queue, done_queue)

for _ in range(1000):
    download_queue.put(object())

stop_threads(download_queue, download_threads)
stop_threads(resize_queue, resize_threads)
stop_threads(upload_queue, upload_threads)

print(done_queue.qsize(), 'items finished')
