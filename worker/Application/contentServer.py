import socket
import copy
import os
import librosa
from soundfile import SoundFile

def convKey(key):
    key = set(list(key))
    key = [ord(e) for e in key]
    key.sort()
    return key

def genInd(key, limit):
    c = 1
    ind = []
    while(True):
        temp = [i*c for i in key]
        if(any(c>limit for c in temp)):
            break
    
        ind += temp
        c += 500
    
    ind.sort()
    return ind

def encDec(data, ind):
    start = 0
    sec = 1
    for i in ind:
        stop = i
        if sec%2==0:
            data[start:stop] = data[start:stop][::-1]   

        start = stop
        sec += 1

    stop = len(data)
    if sec%2==0:
        data[start:stop] = data[start:stop][::-1]
        
    return data

x,sr = librosa.load('./fileStorage/enc.wav', sr=44100)
print("Encoded file loaded!")
y = copy.deepcopy(x)
limit = len(x)
key = 'aez16'
print("Operation key obtained")
key = convKey(key)
ind = genInd(key, limit)
y = encDec(y, ind)
tb = y.tobytes()

with open('./temp/temp.txt', 'wb') as f:
    f.write(tb)

print("Decoded bytes ready for transfer!")
port = 50001
s = socket.socket()
host = socket.gethostbyname('localhost')
s.bind((host, port))
s.listen(5)
print("\nServer listening...")

while True:
    conn, addr = s.accept() 
    f = open('./temp/temp.txt','rb')
    l = f.read(1024)
    while (l):
        conn.send(l)
        l = f.read(1024)
    
    break

f.close()
print("\nData transfer complete!")
conn.close()
s.close()
os.remove('./temp/temp.txt')