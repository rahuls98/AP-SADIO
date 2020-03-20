from flask import Flask, render_template, request, redirect, url_for
import os, random, copy, socket
import pyaudio, wave, sys
import librosa
import soundfile as sf
from soundfile import SoundFile

SRCPATH  = ''
DESTPATH = ''
TEMPPATH = ''
EDK      = ''
TEMPEDK  = ''

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

#############################
##### Utility functions #####
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

##################
##### Routes #####

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
            
            outPath = os.path.join('static/audio/', 'enc.wav')
            librosa.output.write_wav(outPath, y, sr)
            sf.write(outPath, y, sr, subtype='PCM_16')

            global SRCPATH
            global DESTPATH
            global EDK

            SRCPATH = path
            DESTPATH = outPath
            EDK = request.form["EDK"]

    return redirect(url_for('playground'))

@app.route('/playground')
def playground():
    print(SRCPATH, DESTPATH, EDK)
    return render_template('playground.html', upload=SRCPATH, modified=DESTPATH, edk=EDK)

@app.route('/recrypt', methods=['POST'])
def recrypt():
    src = SRCPATH
    
    x,sr = librosa.load(src, sr=44100)
    y = copy.deepcopy(x)
    limit = len(x)

    key = convKey(request.form["EDK"])
    ind = genInd(key, limit)
    y = encDec(y, ind)

    outPath = os.path.join('static/temp/', 'temp.wav')
    librosa.output.write_wav(outPath, y, sr)
    sf.write(outPath, y, sr, subtype='PCM_16')

    global TEMPPATH
    global TEMPEDK
    TEMPPATH = outPath
    TEMPEDK = request.form["EDK"]

    print(EDK, TEMPEDK)
    return redirect(url_for('playground2'))

@app.route('/playground2')
def playground2():
    return render_template('playground.html', upload=SRCPATH, modified=TEMPPATH, edk=TEMPEDK)

@app.route('/library')
def library():
    return render_template('library.html')

@app.route('/player')
def player():
    global DESTPATH
    global EDK

    print(DESTPATH, EDK)

    y,sr = librosa.load(DESTPATH, sr=44100)
    z = copy.deepcopy(y)
    limit = len(y)


    key = convKey(EDK)
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
    return redirect(url_for('library'))

if __name__ == '__main__':
    app.run(debug=True)