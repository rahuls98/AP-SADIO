from flask import Flask, render_template, request, redirect, url_for
import os, random, copy, socket
import pyaudio, wave, sys
import librosa
import soundfile as sf
from soundfile import SoundFile

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

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

@app.route('/home')
def home():
    upload = 'static/uploads/Violin.wav'
    modified = 'static/audio/test.wav'
    edk = 'test'
    return render_template('home.html', upload=upload, modified=modified, edk=edk)

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/form_handler', methods=['POST'])
def form_handler():
    if request.method == "POST":
        if request.files:
            audioUpload = request.files["audioUpload"]
            path = os.path.join('static/uploads/', audioUpload.filename)
            audioUpload.save(path)
            
            x,sr = librosa.load(path, sr=44100)
            y = copy.deepcopy(x)
            limit = len(x)

            key = convKey(request.form["EDK"])
            ind = genInd(key, limit)
            y = encDec(y, ind)
            
            outPath = os.path.join('static/audio/', 'test.wav')
            librosa.output.write_wav(outPath, y, sr)
            sf.write(outPath, y, sr, subtype='PCM_16')

    return redirect(url_for('home'))

@app.route('/demoLib')
def demoLib():
    return render_template('library.html')

@app.route('/player')
def player():
    y,sr = librosa.load('static/audio/test.wav', sr=44100)
    z = copy.deepcopy(y)
    limit = len(y)

    key = convKey('elephant')
    ind = genInd(key, limit)
    z = encDec(z, ind)
    tb = z.tobytes()

    with open('static/temp/temp.txt', 'wb') as f:
        f.write(tb)

    CHUNK = 1024
    wf = open('static/temp/temp.txt', 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format= 1,
                channels=1,
                rate=44100,
                output=True)

    data = wf.read(CHUNK)
    while data != b'':
        stream.write(data)
        data = wf.read(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()
    print('Done')
    os.remove("static/temp/temp.txt")
    return redirect(url_for('demoLib'))

if __name__ == '__main__':
    app.run(debug=True)