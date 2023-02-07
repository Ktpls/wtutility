from utilref import win32api
dur=100
freqseq=[500,750,400]
[win32api.Beep(f,dur) for f in freqseq]