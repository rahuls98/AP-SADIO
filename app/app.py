from flask import Flask, render_template, request, redirect, url_for
import os, random, copy
import pyaudio, wave, sys
import librosa

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
        c += 269
    
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

@app.route('/play')
def play():
    CHUNK = 1024
    wf = wave.open('static/uploads/Violin.wav', 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()
    return 'Playing!'

@app.route('/form-handler', methods=['POST'])
def handle_data():
    if request.method == "POST":
        if request.files:
            audioUpload = request.files["audioUpload"]
            path = os.path.join('static/uploads/', audioUpload.filename)
            audioUpload.save(path)
            
            x,sr = librosa.load(path)
            y = copy.deepcopy(x)
            limit = len(x)

            key = convKey(request.form["EDK"])
            ind = genInd(key, limit)
            y = encDec(y, ind)
            
            outPath = os.path.join('static/audio/', 'test.wav')
            librosa.output.write_wav(outPath, y, sr)

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)