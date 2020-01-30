import pyaudio
import wave
import time

NUM_FRETS = 44

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "/Users/rick/Documents/Other/ampyant/guitar_tones/%d.wav"
 
def main():

    audio = pyaudio.PyAudio()
 
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK, start=False)

    fret = 0
    while fret < NUM_FRETS:
        c = input("recording fret %d when ready...('q' to quit, 'r' to redo): " % fret)
        if c == "q":
            break
        elif c == "r" and fret > 0:
            fret -= 1
        
        print("recording fret %d in " % fret, end="", flush=True)
        for i in range(3, 0, -1):
            print("%d..." % i, end="", flush=True)
            time.sleep(1)
        print("\nrecording now...")

        frames = []
     
        stream.start_stream()
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("finished recording")
        stream.stop_stream()

        waveFile = wave.open(WAVE_OUTPUT_FILENAME % fret, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()
        
        fret += 1

    # stop Recording
    stream.close()
    audio.terminate()


if __name__ == "__main__":
    main()
