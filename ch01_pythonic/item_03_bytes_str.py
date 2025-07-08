# 項目3 bytesとstrの違いを知っておく

# Pythonでは文字列を表すのにbytesとstrの2種類が存在する.
a = b'h\x65llo'
print(list(a))
print(a)

a = 'a\u0300 props'
print(list(a))
print(a)

# strインスタンスはバイナリエンコーディングを持たない
# bytesインスタンスはテキストエンコーディングを持たない

# Unicodeデータをバイナリデータに変換するには, strのencodeメソッドを使う
a = "井上真一"
print(a.encode())

# バイナリデータをUnicodeデータに変換するには, bytesのdecodeメソッドを使う
a = b'hello'
print(a.decode())

'''bytes or str -> str'''
def to_str(bytes_or_str: bytes | str) -> str:
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value

print(repr(to_str(b"foo")))
print(repr(to_str('bar')))

'''bytes or str -> bytes'''
def to_bytes(bytes_or_str: bytes | str) -> bytes:
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value

print(repr(to_bytes(b'foo')))
print(repr(to_bytes('bar')))



# 問題１：同じように動作するbytesとstrを一緒に使えるとは限らない
print(b'one' + b'two')
print('one' + 'two')

# strとbytesは結合できない
# b'one' + 'two'
# 'one' + b'two'

print('---')

# bytes同士, str同士の大小比較は可能
assert b'red' > b'blue'
assert 'red' > 'blue'

# strとbytesの大小比較はできない
# b'red' > 'blue'
# 'red' > b'blue'

# bytesとstrを等しいかどうか調べると同じ文字列(Asciiのfoo)であっても評価結果はFalseになる
print(b'foo' == 'foo') # つまり, bytesとstrを混ぜて演算子をつかってはいけない

print(b'red %s' % b'blue')
print('red %s' % 'blue')

print('---')

# bytesとstrを混ぜてprintは無理
# print(b'red %s' % 'blue')
print('red %s' % b'blue') # __repr__でbytesインスタンスはb'XXX'という文字列に変換されてしまう


# 問題２：(組み込み関数のopenで返される)ファイルハンドルを絡む操作では、デフォルトで生のbytesではなくUnicode文字列が必要
# with open('./ch01_pythonic/data.bin', 'w') as f:
#     f.write(b'\xf1\xf2\xf3\xf4\xf5')

with open('./ch01_pythonic/data.bin', 'wb') as f: # バイナリを書き込むにはバイナリモードでオープンする必要がある
    f.write(b'\xf1\xf2\xf3\xf4\xf5')

# with open('./ch01_pythonic/data.bin', 'r') as f:
#     data = f.read()

with open('./ch01_pythonic/data.bin', 'rb') as f:
    data = f.read()
    print(data)

# 文字エンコーディングを指定してファイルオープンできる
with open("./ch01_pythonic/data.bin", 
          'r', 
          encoding='cp1252' # Windows符号化
          ) as f:
    data = f.read()
    print(data)


'''システムのデフォルトロケールをチェック'''
import locale
print(locale.getpreferredencoding())

