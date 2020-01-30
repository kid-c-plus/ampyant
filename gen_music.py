# Author: Eric Lewis

from pydub import AudioSegment
from pydub.playback import play

import threading, queue
import random
import time

WAV_LENGTH = 3000
SAMPLE_LENGTH = 2000
LENGTH_DIFF = WAV_LENGTH - SAMPLE_LENGTH
FADE_LENGTH = SAMPLE_LENGTH // 4

# LENGTH: technically number of discrete notes
MIN_LENGTH = 10
MAX_LENGTH = 43

# DURATION: number of times a SAMPLE_LENGTH worth of note repeats 
MIN_NOTE_DUR = 5
MAX_NOTE_DUR = 20

# LONE DURATION: length of time a note sounds before the next is added
MIN_NOTE_LD = 0
MAX_NOTE_LD = 3

# SCALES: means of deriving a series of notes from a randomly chosen root
SCALES = [
            {'root' : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'mods' : [0, 2, 7, 11, 12, 14, 19, 23, 24, 26, 28, 29, 31]}
         ]

def pick_note_dur():
    return random.randint(MIN_NOTE_DUR, MAX_NOTE_DUR)

def pick_note_ld():
    return random.randint(MIN_NOTE_LD, MAX_NOTE_LD)

def pick_note(root, mods):
    return root + random.randint(0, len(mods) - 1)

# Returns an AudioSegment object containing a single "song"
def write_song(seed=None):
    random.seed(a=seed)
    
    # randomly select length, scale and root

    length = random.randint(MIN_LENGTH, MAX_LENGTH)

    scale = SCALES[random.randint(0, len(SCALES) - 1)]
    root_note = scale['root'][random.randint(0, len(scale['root']) - 1)]

    # notes must all be precomputed in order to determine length of silent root AudioSegment
    # note notation: [pitch, duration, lone duration]
    total_dur = max(pick_note_ld(), 2)
    note_dur = max(pick_note_dur(), total_dur)
    curr_trail = note_dur
    notes = [[root_note, note_dur, total_dur]]

    prev_note = root_note

    for _ in range(length - 2):
        note = prev_note
        while note == prev_note:
            note = pick_note(root_note, scale['mods'])
        prev_note = note
        ld = pick_note_ld()
        note_dur = max(pick_note_dur(), ld)
     
        total_dur += ld

        # determines how long all notes will continue out from the point where the current note is added
        # important because I want the root note to sound last
        curr_trail -= ld
        if curr_trail < note_dur:
            curr_trail = note_dur

        notes.append([pick_note(root_note, scale['mods']), note_dur, ld])
    
    end_ld = pick_note_ld()

    end_dur = max(pick_note_dur(), end_ld, curr_trail)
    total_dur += end_dur

    notes.append([root_note, end_dur, end_ld])

    # all notes will be overlaid over this silent AudioSegment
    root_seg = AudioSegment.silent(duration = total_dur * SAMPLE_LENGTH)
    
    # curr_overlay: the index used to place the current note, advances with LONE DURATION, not DURATION
    curr_overlay = 0
    for note in notes:
        p, dur, ld = note
        wav_seg = AudioSegment.from_file("guitar_tones/%d.wav" % p)
        note_seg = wav_seg[LENGTH_DIFF // 2: ]
        # appending and crossfading removes the "pops" heard when starting and stopping a file
        for _ in range(dur - 1):
            combined = note_seg.append(wav_seg, crossfade=LENGTH_DIFF)
            note_seg = combined
        note_seg = (note_seg[: -1 * LENGTH_DIFF // 2]).fade_in(FADE_LENGTH).fade_out(FADE_LENGTH)
        root_seg = root_seg.overlay(note_seg, position=curr_overlay)
        curr_overlay += ld * SAMPLE_LENGTH

    return root_seg

def main():
    
    # writes new songs in the background
    # unfortunately, crossfading makes this take a significant amount of time, depending on song length
    def song_worker():
        while True:
            if songs.qsize() < 5:
                print("writing a new song...")
                songs.put(write_song())
            else:
                time.sleep(0.25)

    songs = queue.Queue()
    
    cv = threading.Condition()
    song_thread = threading.Thread(target=song_worker)
    song_thread.start()

    while True:
        song = songs.get()
        print("playing a new song!")
        play(song)

if __name__ == "__main__":
    main()
        
