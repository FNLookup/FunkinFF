import json
import mido

def groupNotesByTimes(time,notes):
    foundNotes = []

    for note in notes:
        if abs(time - note['t']) <= 1:
            foundNotes.append(note)

    return foundNotes

def get_tempo(time, tempo_times):
    if not tempo_times:
        return None  # Handle empty tempo_times list

    # Check first tempo without decrementing i
    if time <= tempo_times[0]['t']:
        return tempo_times[0]

    for i, tempo_change in enumerate(tempo_times[1:], start=1):
        check = i - 1
        if tempo_times[check]['t'] <= time and tempo_change['t'] >= time:
            return tempo_times[check]
    # Return last tempo if no match is found
    return tempo_times[-1]

# length of a beat: 535ms
# bpm=112

def altCode():
    trackInfos = [
        {
            "midi-track-name": "PLASTIC DRUMS",
            "track-variation-suffix": "-drums",
            "track-difficulty-prefix": "pro-",
            "istap": False
        },
        {
            "midi-track-name": "PLASTIC GUITAR",
            "track-variation-suffix": "-guitar",
            "track-difficulty-prefix": "pro-",
            "istap": False
        },
        {
            "midi-track-name": "PLASTIC BASS",
            "track-variation-suffix": "-bass",
            "track-difficulty-prefix": "pro-",
            "istap": False
        },
        {
            "midi-track-name": "PART VOCALS",
            "track-variation-suffix": "",
            "track-difficulty-prefix": "",
            "istap": True
        },
        {
            "midi-track-name": "PART GUITAR",
            "track-variation-suffix": "-guitar",
            "track-difficulty-prefix": "",
            "istap": True
        },
        {
            "midi-track-name": "PART DRUMS",
            "track-variation-suffix": "-drums",
            "track-difficulty-prefix": "",
            "istap": True
        },
        {
            "midi-track-name": "PART BASS",
            "track-variation-suffix": "-bass",
            "track-difficulty-prefix": "",
            "istap": True
        },
        {
            "midi-track-name": "SECTION",
            "track-variation-suffix": "-section",
            "track-difficulty-prefix": "",
            "istap": True
        },
        {
            "midi-track-name": "BEAT",
            "track-variation-suffix": "-beat",
            "track-difficulty-prefix": "",
            "istap": True,
            "track_is_special": True
        },
        {
            "midi-track-name": "EVENTS",
            "track-variation-suffix": "-events",
            "track-difficulty-prefix": "",
            "istap": True
        }
    ]

    bpm = 109.99990833340972

    beatCrochetMs = (60 / bpm) * 1000

    stepCrochetMs = beatCrochetMs / 4

    ticksPerBeat = 480

    midi = mido.MidiFile()
    midi.ticks_per_beat = ticksPerBeat

    for track in trackInfos:
        trackSuffixFile = track['track-variation-suffix']
        trackDiffPrefix = track['track-difficulty-prefix']
        trackMidiName = track['midi-track-name']
        isTrackTap = track['istap']

        trackIsSpecial = track.get('track_is_special', False)

        midiTrack = mido.MidiTrack()
        midiTrack.name = trackMidiName

        #trackMeta = json.loads(open('_fnfc/partypacker-metadata-guitar.json', 'r').read())
        trackNotes = json.loads(open(f'_fnfc/partypacker-chart{trackSuffixFile}.json', 'r').read())

        trackNotes_easy = trackNotes['notes'].get(f'{trackDiffPrefix}easy', [])
        trackNotes_medi = trackNotes['notes'].get(f'{trackDiffPrefix}medium', [])
        trackNotes_hard = trackNotes['notes'].get(f'{trackDiffPrefix}hard', [])
        trackNotes_expe = trackNotes['notes'].get(f'{trackDiffPrefix}expert', [])

        trackEvents = trackNotes['events']
        
        timedNotes = processTimes(
            [trackNotes_easy,
            trackNotes_medi,
            trackNotes_hard,
            trackNotes_expe], 
            isTrackTap, 
            stepCrochetMs,
            trackEvents,
            trackIsSpecial,
            trackMidiName
        )

        lastEventTime = 0

        for event in timedNotes:
            eventTime = event['time'] - lastEventTime

            beatsSince = 0
            try:
                beatsSince = eventTime / beatCrochetMs
            except:
                print('Some unknown error')

            #print(f'{eventTime = } \n{event['data']  = } \n{event['event']  = }\n{beatsSince = }')

            ticksSince = round(beatsSince * ticksPerBeat)
            
            if ticksSince < 0:
                print(f'Fuck you i found a dumbass thats negative {ticksSince}')
                return

            message = None

            if event['event'].startswith('note'):
                message = mido.Message(event['event'], time=ticksSince, velocity=96, note=event['data'])
            if event['event'] == 'text':
                message = mido.MetaMessage(event['event'], time=ticksSince, text=event['data'])
            
            if message:
                midiTrack.append(message)
            else: # Avoid setting the next event time because we couldnt add this event to midi
                continue

            lastEventTime = event['time']

        midi.tracks.append(midiTrack)

    midi.save('testmidi.mid')

def processTimes(tracks = [], isTap = True, defaultNoteDuration = 100, events = [], trackIsSpecial = False, trackName = 'NOT SET'):
    notesSortedAsEvents = []

    liftThreshold = 6

    midiKeys_Tap = [ # Non-plastic
        {   # Track 0, EASY
            0: 60,
            1: 61,
            2: 62,
            3: 63
        },
        {   # Track 1, MEDIUM
            0: 72,
            1: 73,
            2: 74,
            3: 75
        },
        {   # Track 2, HARD
            0: 84,
            1: 85,
            2: 86,
            3: 87
        },
        {   # Track 3, EXPERT
            7: 96,
            0: 97,
            1: 98,
            2: 99,
            3: 100,
            4: 116 # Overdrive
        }
    ]

    midiKeys_Plastic = [ # plastic track
        {   # Track 0, EASY
            7: 60,
            0: 61,
            1: 62,
            2: 63,
            3: 64
        },
        {   # Track 1, MEDIUM
            7: 72,
            0: 73,
            1: 74,
            2: 75
        },
        {   # Track 2, HARD
            7: 84,
            0: 85,
            1: 86,
            2: 87,
            3: 88
        },
        {   # Track 3, EXPERT
            7: 96,
            0: 97,
            1: 98,
            2: 99,
            3: 100,
            4: 116 # Overdrive
        }
    ]

    midiKeysTemplate = midiKeys_Tap if isTap else midiKeys_Plastic

    if trackIsSpecial:
        midiKeysTemplate = [ # BEAT track notes
            {
                4: 12,
                0: 13
            },
            {}, {}, {}
        ]

    for i, track in enumerate(tracks):
        for j, note in enumerate(track):
            strumTime = note['t']
            noteData = note['d']
            susLength = note['l']

            noteKey = midiKeysTemplate[i].get(noteData, 0)

            if noteKey == 0:
                print(f'Could not find note for {noteData} in difficulty {i} of track {trackName}, ignoring')
                continue

            if susLength <= 0:
                # Apply a default length, since midi needs it
                susLength = defaultNoteDuration

            notesSortedAsEvents.append({
                "time": strumTime,
                "data": noteKey,
                "event": "note_on"
            })

            notesSortedAsEvents.append({
                "time": strumTime + susLength,
                "data": noteKey,
                "event": "note_off"
            })

            if note.get('k', '') == 'Lift':
                notesSortedAsEvents.append({
                    "time": strumTime,
                    "data": noteKey + liftThreshold,
                    "event": "note_on"
                })

                notesSortedAsEvents.append({
                    "time": strumTime + susLength,
                    "data": noteKey + liftThreshold,
                    "event": "note_off"
                })

    for event in events:
        eventTime = event['t']
        eventType = event['v']['type']
        eventText = event['v']['text']
        eventIsTapEvent = not event['v']['plastic_track']

        # Check the boolean plastic track
        if isTap == eventIsTapEvent:
            if eventType != 'text':
                eventText = eventType

            notesSortedAsEvents.append({
                "time": eventTime,
                "data": eventText,
                "event": "text"
            })

    return sorted(notesSortedAsEvents, key=lambda note: note['time'])

altCode()