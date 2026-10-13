import json,urllib.request,urllib.parse
E='http://127.0.0.1:50021'
def synth(text, vid, speed=1.1, pitch=-0.03, inton=1.0, out=None):
    q=json.loads(urllib.request.urlopen(urllib.request.Request(E+'/audio_query?'+urllib.parse.urlencode({'text':text,'speaker':vid}),method='POST')).read())
    q.update(speedScale=speed,pitchScale=pitch,intonationScale=inton,prePhonemeLength=0.03,postPhonemeLength=0.05,outputSamplingRate=48000,outputStereo=True)
    w=urllib.request.urlopen(urllib.request.Request(E+f'/synthesis?speaker={vid}',data=json.dumps(q).encode(),headers={'Content-Type':'application/json'})).read()
    if out: open(out,'wb').write(w)
    return w
