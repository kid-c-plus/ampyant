from pydub import AudioSegment
from pydub.playback import play

import random

WAV_LENGTH = 3000
SAMPLE_LENGTH = 2000
LENGTH_DIFF = WAV_LENGTH - SAMPLE_LENGTH
FADE_LENGTH = SAMPLE_LENGTH // 4

MIN_LENGTH = 10
MAX_LENGTH = 43
MIN_NOTE_DUR = 5
MAX_NOTE_DUR = 20
MIN_NOTE_LD = 0
MAX_NOTE_LD = 3

SCALES = [
            {'root' : [0, 1, 2, 3, 4],
            'mods' : [0, 2, 7, 11, 12, 14, 19, 23, 24, 26, 28, 29, 31]}
         ]

def pick_note_dur():
    return random.randint(MIN_NOTE_DUR, MAX_NOTE_DUR)

def pick_note_ld():
    return random.randint(MIN_NOTE_LD, MAX_NOTE_LD)

def pick_note(root, mods):
    return root + random.randint(0, len(mods) - 1)

def write_song(seed=None):
    random.seed(a=seed)
    
    length = random.randint(MIN_LENGTH, MAX_LENGTH)

    scale = SCALES[random.randint(0, len(SCALES) - 1)]
    root = scale['root'][random.randint(0, len(scale['root']) - 1)]

    # note notation: [pitch, duration, lone duration]
    total_dur = max(pick_note_ld(), 2)
    note_dur = max(pick_note_dur(), total_dur)
    curr_trail = note_dur
    notes = [[root, note_dur, total_dur]]

    for _ in range(length - 2):
        ld = pick_note_ld()
        note_dur = max(pick_note_dur(), ld)
     
        total_dur += ld

        curr_trail -= ld
        if curr_trail < note_dur:
            curr_trail = note_dur

        notes.append([pick_note(root, scale['mods']), note_dur, ld])
    
    end_ld = pick_note_ld()

    end_dur = max(pick_note_dur(), end_ld, curr_trail)
    total_dur += end_dur

    notes.append([root, end_dur, end_ld])

    root_seg = AudioSegment.silent(duration = total_dur * SAMPLE_LENGTH)
    
    curr_overlay = 0
    for note in notes:
        p, dur, ld = note
        note_seg = (AudioSegment.from_file("guitar_tones/%d.wav" % p).fade_in(LENGTH_DIFF).fade_out(LENGTH_DIFF)[LENGTH_DIFF // 2: -1 * LENGTH_DIFF // 2] * dur).fade_in(FADE_LENGTH).fade_out(FADE_LENGTH)
        root_seg = root_seg.overlay(note_seg, position=curr_overlay)
        curr_overlay += ld * SAMPLE_LENGTH

    return root_seg

def main():
    while True:
        play(write_song())
        if input("wanna hear another? (y/n)\n") == "n":
            break

if __name__ == "__main__":
    main()
        
