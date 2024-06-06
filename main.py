import copy
import json
from pydub import AudioSegment
from pathlib import Path
import shutil
import window
import midotest as midotool

def assignFfmpeg(audiosegment:AudioSegment):
    ffmpeg_path = Path('ffmpeg/ffmpeg.exe')

    if Path.exists(ffmpeg_path):
        ffmpeg_to_use = str(ffmpeg_path.resolve()).replace('\\', '/').replace('.exe', '')

    audiosegment.converter = ffmpeg_to_use

def assignFfmpegBulk(audiosegments:list):
    print('Assigning ffmpeg bulk to a list')
    for audiosegment in audiosegments:
        assignFfmpeg(audiosegment)

def audioSegmentFromFile(file):
    print('Opening file ' + file + ' as a new AudioSegment')
    return AudioSegment.from_file(file, format="ogg")

def createFolder(folder_path):
    if not Path(folder_path).exists():
        try:
            Path(folder_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f'Something went wrong: {e}')
    else:
        print(f'{folder_path} already exists!')

def overlayAndExport(backing:AudioSegment, segmentsInst, segmentsVocal, suffix:str):
    inst = AudioSegment.silent(duration=len(backing))
    vocalsBF = AudioSegment.silent(duration=len(backing))

    assignFfmpegBulk([inst, vocalsBF])

    inst = inst.overlay(backing, position=0)

    for instseg in segmentsInst:
        print('Overlaying a track to instrumental')
        inst = inst.overlay(instseg, position=0)

    for vocseg in segmentsVocal:
        print('Overlaying a track to vocals')
        vocalsBF = vocalsBF.overlay(vocseg, position=0)

    inst.export(f'_fnfc/Inst{suffix}.ogg', format="ogg")
    vocalsBF.export(f'_fnfc/Voices{suffix}-bf.ogg', format="ogg")

def toZip(pathbase,fnfc_name):
    _final_pathbase = pathbase + '/festcharter/'
    createFolder(_final_pathbase)
    shutil.make_archive(f'{_final_pathbase}{fnfc_name}', 'zip', '_fnfc/')
    fnfcPath = Path(f'{_final_pathbase}{fnfc_name}.zip')
    fnfcPath.rename(f'{_final_pathbase}{fnfc_name}.fnfc')
    #fnfcPath.unlink()

    #shutil.rmtree('_fnfc/')

assignFfmpegBulk([AudioSegment])

# Load tracks



# assignFfmpegBulk([backing, vocals, drums, guitar, bass])

# overlayAndExport(backing, [drums, guitar, bass], [vocals], 'TEST_FNFC')

def makeFnfcFile(backingPath, vocalsPath, drumsPath, guitarPath, bassPath, fnfcName, pathWhereToSaveFnfc, midiFile):
    createFolder('_fnfc/')
    print(backingPath, vocalsPath, drumsPath, guitarPath, bassPath)
    print('Saving ' + fnfcName + ' to ' + pathWhereToSaveFnfc)

    backing = audioSegmentFromFile(backingPath)

    songkey = 'partypacker'

    arrayOfPaths = [drumsPath, guitarPath, bassPath, vocalsPath]
    variants = [
        '-drums',
        '-guitar',
        '-bass',
        '' # This is the default variation!! (Vocals)
    ]

    for path in arrayOfPaths:
        if len(path) < 1:
            continue

        vocals = []
        instAudios = []

        for apath in arrayOfPaths:
            if len(apath) < 1:
                continue

            # instrumental 
            if apath != path:
                instAudios.append(audioSegmentFromFile(apath))
            else:
                vocals = [audioSegmentFromFile(apath)]

        overlayAndExport(backing, instAudios, vocals, variants[arrayOfPaths.index(path)])

    diffs = [
        'easy',
        'medium',
        'hard',
        'expert'
    ]
    diffs_pro = [
        'pro-easy',
        'pro-medium',
        'pro-hard',
        'pro-expert'
    ]
    variations = [
        'drums',
        'guitar',
        'bass',
        'events',
        'beat',
        'section'
    ]

    allowed_events = [
        '[music_start]',
        '[music_end]',
        '[preview]',
        '[end]',
        '[idle_realtime]',
        '[idle_mellow]',
        '[idle_intense]',
        '[idle]',
        '[mellow]',
        '[play]',
        '[intense]',
        '[pickup]',
        '[guitar]',
        '[keytar]',
        '[intro]',
        '[verse]',
        '[build]',
        '[chorus]',
        '[prechorus]',
        '[breakdown]',
        '[bridge]',
        '[drop]',
        '[solo_guitar]',
        '[solo_drums]',
        '[solo_voice]',
        '[solo_bass]',
        '[outro]'
    ]

    BASE_META = {
        "version": "2.2.2",
        "songName": "Festival Format Song",
        "artist": "Unknown",
        "looped": False,

        "offsets": {
            "instrumental": 0,
            "altInstrumentals": {},
            "vocals": {}
        },

        "playData": {
            "album": "volume1",
            "previewStart": 0,
            "previewEnd": 15000,
            "songVariations": variations,
            "difficulties": diffs + diffs_pro,
            "characters": {
                "album": "volume1",
                "player": "bf",
                "girlfriend": "gf",
                "opponent": "dad",
                "instrumental": "",
                "altInstrumentals": []
            },
            "stage": "mainStage",
            "noteStyle": "funkin",
            "ratings": {}
        },
        "timeFormat": "ms",
        "timeChanges": [],
        "generatedBy": "Festival Charter"
    }

    BASE_CHART = {
        "version": "2.0.0",
        "scrollSpeed": {
            "default": 2.0
        },
        "events": [],
        "notes": {},
        "generatedBy": "Festival Charter"
    }

    festivalNotes = {
        "tempo": [],
        "time_signature": [],
        'tracks': []
    }
    if len(midiFile) > 0:
        festivalNotes = midotool.midi_to_object(midiFile)

    for specialTrack in ['events', 'beat', 'section']:
        metadataFileName = songkey + '-metadata-' + specialTrack + '.json'
        chartFileName = songkey + '-chart-' + specialTrack + '.json'

        metaObj = copy.deepcopy(BASE_META)
        chartObj = copy.deepcopy(BASE_CHART)

        metaObj['playData']['songVariations'] = []

        for tempoChange in festivalNotes['tempo']:
            metaObj['timeChanges'].append({
                "t": tempoChange['time'],
                "bpm": tempoChange['bpm'],
                "n": 4,
                "d": 4,
                "bt": [4] * 4
            })

        chartObj['notes']['events'] = []

        for track in festivalNotes['tracks']:
            if track['name'] == specialTrack.upper():
                for event in track['events']:
                    eventObject = {
                        "t": event['time'],
                        "e": "MIDI Event",
                        "v": {
                        "type": event['text'] if event['text'] in allowed_events else 'text',
                        "text": event['text'],
                        "plastic_track": False }
                    }

                    if event['text'] in allowed_events:
                        eventObject['type'] = event['text']

                    chartObj['events'].append(eventObject)
                    
        if specialTrack == 'beat':
            metaObj['playData']['difficulties'] += ['ticks']
            for track in festivalNotes['tracks']:
                if track['name'] == 'BEAT':
                    for tick in track['notes']:
                        tick_time = tick['start_time']
                        tick_key = tick['note']
                        tick_duration = tick['duration']

                        ntdtmap = {
                            12: 4,
                            13: 0
                        }

                        if 'easy' not in chartObj['notes']:
                            chartObj['notes']['easy'] = []
                        else:
                            chartObj['notes']['easy'].append(
                                {"d": ntdtmap[tick_key], "l": tick_duration, "t": tick_time})

        with open('_fnfc/' + metadataFileName, 'w') as metadataJson:
            metadataJson.write(json.dumps(metaObj, indent=4))

        with open('_fnfc/' + chartFileName, 'w') as chartJson:
            chartJson.write(json.dumps(chartObj, indent=4))

    for variant in variants:
        metadataFileName = songkey + '-metadata' + variant + '.json'
        chartFileName = songkey + '-chart' + variant + '.json'

        metaObj = copy.deepcopy(BASE_META)
        chartObj = copy.deepcopy(BASE_CHART)
        diffsToUse = diffs + diffs_pro

        if variant != '': # Vocal
            metaObj['playData']['songVariations'] = []

        for tempoChange in festivalNotes['tempo']:
            metaObj['timeChanges'].append({
                "t": tempoChange['time'],
                "bpm": tempoChange['bpm'],
                "n": 4,
                "d": 4,
                "bt": [4] * 4
            })
        
        trackEventsPlacedInChart = []

        for diff in diffsToUse:
            original_key_ranges = [
                [60, 61, 62, 63, 64],
                [72, 73, 74, 75, 76],
                [84, 85, 86, 87, 88],
                [96, 97, 98, 99, 100, 116] # For commodity, the overdrive activations are charted on the Expert difficulty.
            ]

            original_lift_key_ranges = [
                [66, 67, 68, 69, 70],
                [78, 79, 80, 81, 82],
                [90, 91, 92, 93, 94],
                [102, 103, 104, 105, 106]
            ]

            key_ranges = []
            lift_note_ranges = []

            should_shift_notes_1_left = False

            if variant == '-drums':
                festTrack = 'PART DRUMS'
                if diff.startswith('pro'):
                    festTrack = 'PLASTIC DRUMS'
            if variant == '-bass':
                festTrack = 'PART BASS'
                if diff.startswith('pro'):
                    festTrack = 'PLASTIC BASS'
            if variant == '-guitar':
                festTrack = 'PART GUITAR'
                if diff.startswith('pro'):
                    festTrack = 'PLASTIC GUITAR'
            if variant == '':
                festTrack = 'PART VOCALS'

            if diff.startswith('pro') or diff.endswith('expert'):
                should_shift_notes_1_left = True

            if diff.endswith('easy'):
                key_ranges = original_key_ranges[0]
                lift_note_ranges = original_lift_key_ranges[0]
            if diff.endswith('medium'):
                key_ranges = original_key_ranges[1]
                lift_note_ranges = original_lift_key_ranges[1]
            if diff.endswith('hard'):
                key_ranges = original_key_ranges[2]
                lift_note_ranges = original_lift_key_ranges[2]
            if diff.endswith('expert'):
                key_ranges = original_key_ranges[3]
                lift_note_ranges = original_lift_key_ranges[3]

            baseNotes = []
            trackNotes = []
            trackEvents = []
            for track in festivalNotes['tracks']:
                if track['name'] == festTrack:
                    trackEvents = track['events']
                    trackNotes = track['notes']

            if festTrack not in trackEventsPlacedInChart:
                for event in trackEvents:
                    #print('Placed event ' + event['text'] + ' of track ' + festTrack)
                    eventObject = {
                        "t": event['time'],
                        "e": "MIDI Event",
                        "v": {
                        "type": event['text'] if event['text'] in allowed_events else 'text',
                        "text": event['text'],
                        "plastic_track": festTrack.startswith('PLASTIC') }
                    }

                    print(f'Placing event:\n{eventObject}')

                    chartObj['events'].append(eventObject)

                trackEventsPlacedInChart.append(festTrack)

            prevNoteData = 0
            prevNoteTime = 0

            for note in trackNotes:
                #print(note)
                if note['note'] in key_ranges + lift_note_ranges:
                    sustainLength = 0

                    if note['is_hold_note']:
                        sustainLength = note['duration']

                    strumTime = note['start_time']
                    should_add_lift_note_kind = False

                    baseNote = {}
                    noteData = 7 ## Dad Right

                    if note['note'] in key_ranges: # Normal
                        noteData = note['note'] - key_ranges[0]

                        prevNoteData = noteData
                        prevNoteTime = note['start_time']

                    elif note['note'] in lift_note_ranges: # lift
                        noteData = note['note'] - lift_note_ranges[0]

                        if abs(prevNoteTime - note['start_time']) < 2 and prevNoteData == noteData: # Eliminates the last note with the nearest matching time of 2ms
                            lastRealNote = baseNotes.pop()
                            strumTime = lastRealNote['t']
                            print('Eliminated a note to give in for a lift')

                            should_add_lift_note_kind = True

                    # In hard,easy,medium diffs will not shift
                    if should_shift_notes_1_left:
                        noteData -= 1
                        # Dad notes range from 4 to 7, so the left expert lane would be at 7
                        if noteData == -1:
                            noteData = 7

                    if note['note'] in key_ranges:
                        # Checks if there is an extra value at the end for the overdrive markers
                        if key_ranges.index(note['note']) == len(key_ranges) - 1 and len(key_ranges) == 6:
                            # Overdrive note
                            print('Overdrive note!')
                            noteData = 4

                    baseNote = {"d": noteData, "l": sustainLength, "t": strumTime}
                    if should_add_lift_note_kind:
                        baseNote = {"d": noteData, "l": sustainLength, "t": strumTime, "k": "Lift"}

                    print(baseNote)

                    baseNotes.append(baseNote)

            chartObj['notes'][diff] = baseNotes

        with open('_fnfc/' + metadataFileName, 'w') as metadataJson:
            metadataJson.write(json.dumps(metaObj, indent=4))

        chartObj['events'].sort(key=lambda event: event['t'])

        with open('_fnfc/' + chartFileName, 'w') as chartJson:
            chartJson.write(json.dumps(chartObj, indent=4))

    with open('_fnfc/manifest.json', 'w') as manifestFile:
        manifestFile.write(json.dumps({
            "version": "1.0.0",
            "songId": songkey
        }, indent=4))

    toZip(pathWhereToSaveFnfc, fnfcName)

    return 'festcharter/' + fnfcName + '.fnfc'

if __name__ == '__main__':
    window.init()