# 子プロセスの生成にはsubprocessを使うべき
# 1. 一回限りの子プロセス実行には, run()メソッドを使う
# 2. Popenクラスを用いると, メインプロセスで他のタスクを実行しながら子プロセスを定期的にポーリングしてチェックできる

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
import subprocess
# Enable these lines to make this example work on Windows
# import os
# os.environ['COMSPEC'] = 'powershell'

result = subprocess.run(
    ['echo', 'Hello from the child'],
    capture_output=True,
    # Enable this line to make this example work on Windows
    # shell=True,
    encoding='utf-8')

result.check_returncode() # No exception means it exited cleanly
print(result.stdout)

# Example 2
# Use this line instead to make this example work on Windows
# proc = subprocess.Popen(['sleep', '1'], shell=True)
proc = subprocess.Popen(['sleep', '1'])
while proc.poll() is None:
    print('Working...')
    # Some time-consuming work here
    import time
    time.sleep(0.3)

print("Exit status", proc.poll())

# Example 3
import time

start = time.time()
sleep_procs = []
for _ in range(10):
    # Use this line instead to make this example work on Windows
    # proc = subprocess.Popen(['sleep', '1'], shell=True)
    proc = subprocess.Popen(['sleep', '1'])
    sleep_procs.append(proc)

# Example 4
for proc in sleep_procs:
    proc.communicate() # threading.Threadのjoin()と同じ挙動をする

end = time.time()
delta = end - start
print(f"Finished in {delta:.3} [s]")


# Example 5
import os
# On Windows, after installing OpenSSL, you may need to
# alias it in your Powershell path with a comamnd like:
# $env:path = $env:path + "C:\Program Files\OpenSSL-Win64\bin"

def run_encrypt(data):
    env = os.environ.copy()
    env['password'] = 'zf7ShyBhZOraQDdE/FiZpm/m/8f9X+M1'
    proc = subprocess.Popen(
        ['openssl', 'enc', '-des3', '-pass', 'env:password'],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    proc.stdin.write(data)
    proc.stdin.flush()
    return proc

# Example 6
procs = []
for _ in range(3):
    data = os.urandom(10)
    proc = run_encrypt(data)
    procs.append(proc)

# Example 7
for proc in procs:
    out, _ = proc.communicate()
    print(out[-10:])

# Example 8
def run_hash(input_stdin):
    return subprocess.Popen(
        ['openssl', 'dgst', '-whirlpool', '-binary'],
        stdin=input_stdin, # 親プロセスの標準出力を子プロセスの標準入力にパイプする
        stdout=subprocess.PIPE # 子プロセスの標準出力を親プロセスの標準出力にパイプする
    )

# Example 9
encrypt_procs = []
hash_procs = []
for _ in range(3):
    data = os.urandom(100)

    encrypt_proc = run_encrypt(data)
    encrypt_procs.append(encrypt_proc)

    hash_proc = run_hash(encrypt_proc.stdout)
    hash_procs.append(hash_proc)

    # Ensure that child consumes the input stream and
    # the communicate() method dose'nt inadvertently steal
    # input from the child. Also lets SIGPIPE propagate to
    # the upstream process if the downstream process dies.
    encrypt_proc.stdout.close() # 親プロセス経由で子プロセスの標準出力を取り出さないように閉じる
    encrypt_proc.stdout = None

# Example 10
for proc in encrypt_procs:
    proc.communicate() # opensslの暗号化が正常終了しているかチェック
    assert proc.returncode == 0

for proc in hash_procs:
    out, _ = proc.communicate() # 孫プロセスであるハッシュの標準出力から親プロセスにパイプで結果を取り出す
    print(out[-10:])
    assert proc.returncode == 0, f"Return code: {proc.returncode}"

# Example 11
# Use this line instead to make this example work on Windows
# proc = subprocess.Popen(['sleep', '10'], shell=True)
proc = subprocess.Popen(['sleep', '10'])
try:
    proc.communicate(timeout=0.1) # 子/孫プロセスが指定した時間ないに応答がなければタイムアウトで例外発生
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait()

print('Exit status', proc.poll())



