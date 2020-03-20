import socket                
import pyaudio
import wave
import sys

CHUNK = 1024
p = pyaudio.PyAudio()

stream = p.open(format=1,
                channels=1,
                rate=44100,
                output=True)

s = socket.socket()
host = socket.gethostbyname('localhost')
port = 50001
s.connect((host, port))
print("\nReceiving data")

while True:
    data = s.recv(1024)
    if not data:
        break
    stream.write(data)

stream.stop_stream()
stream.close()
p.terminate()
print("\nData streaming complete!")
s.close()
print("Connection closed")