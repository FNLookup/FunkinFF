import time
import mido
import json

def get_length_in_beats(_bpm, ticks_since_last, ppqn):
    #tempo  = mido.bpm2tempo(_bpm)

    #bpm = mido.tempo2bpm(tempo)
    bpm = _bpm

    try:
        beat_crochet = (60 / bpm)
    except:
        beat_crochet = 0
    try:
        length_in_beats_of_note = ticks_since_last / ppqn
    except ZeroDivisionError:
        length_in_beats_of_note = 0

    return beat_crochet * length_in_beats_of_note

def get_length_in_beats_tempo(tempo, ticks_since_last, ppqn):
    try:
        bpm = mido.tempo2bpm(tempo)
    except Exception as e:
        print(f'Failed to make bpm: {e}, tempo is {tempo}')
        bpm = mido.tempo2bpm(500000)
    return get_length_in_beats(bpm, ticks_since_last, ppqn)

def get_tempo(time, tempo_times):
    if not tempo_times:
        return None  # Handle empty tempo_times list

    # Check first tempo without decrementing i
    if time <= tempo_times[0][0]:
        return tempo_times[0]

    for i, tempo_change in enumerate(tempo_times[1:], start=1):
        check = i - 1
        if tempo_times[check][0] <= time and tempo_change[0] >= time:
            return tempo_times[check]
    # Return last tempo if no match is found
    return tempo_times[-1]

# Fortnites ppqn is 480
# A note indicates it lasts 120 ticks because
# 480 / 4 is 120, means 120 is a step
# Then that means it lasted 120 ticks, since its last note_on event
# A note event is then calculated 360 ticks after the last note_off event
# Which is 3 steps

def midi_to_object(midi_file_path):
    mid = mido.MidiFile(midi_file_path)

    #print(mid.ticks_per_beat)
    
    midi_data = {
        'ticks_per_beat': mid.ticks_per_beat,
        "tempo": [],
        "time_signature": [],
        'tracks': []
    }

    # Extract tempo and time signature events
    tempo_times = []

    # Process tempo changes first
    for i, track in enumerate(mid.tracks):
        absolute_time = 0
        ticks_since_last_tempo = 0
        previous_tempo_change_bpm = 0
        tempo_change_times = 0

        for msg in track:
            absolute_time += msg.time
            ticks_since_last_tempo += msg.time

            if msg.type == "set_tempo":
                # To calculate the time at which this tempo change occurs, we use the previous tempo change value.
                # Tempo change times
                tempo_change_times += get_length_in_beats(previous_tempo_change_bpm, ticks_since_last_tempo, mid.ticks_per_beat)

                this_change_bpm = mido.tempo2bpm(msg.tempo)

                midi_data["tempo"].append({
                    # "time_since_last": msg.time,
                    # "time_in_ticks": absolute_time,

                    'time': tempo_change_times * 1000,
                    "bpm": this_change_bpm,
                    "tempo": msg.tempo
                })

                ticks_since_last_tempo = 0

                prev = previous_tempo_change_bpm

                previous_tempo_change_bpm = this_change_bpm

                tempo_times.append([
                                    # the good old absolute time
                                    absolute_time, 
                                    # The bpm
                                    this_change_bpm,
                                    # the time in ms this occurs at 
                                    tempo_change_times, 
                                    # The tempo
                                    msg.tempo, 
                                    # the ticks since the last one it took for this one to occur
                                    msg.time,
                                    # The previous bpm 
                                    prev,
                                    # The beats using the ticks since the last one
                                    msg.time / mid.ticks_per_beat
                                ])

            # if msg.type == "time_signature":
            #     midi_data["time_signature"].append({
            #         "time_since_last": msg.time,
            #         "time_in_ticks": absolute_time,
            #         "time": msg.time,
            #         "numerator": msg.numerator,
            #         "denominator": msg.denominator,
            #         "click": msg.clocks_per_click,
            #         "notesQ": msg.notated_32nd_notes_per_beat
            #     })

    #open('tempos.json', 'w').write(json.dumps(tempo_times, indent=4))

    for i, track in enumerate(mid.tracks):
        track_data = {
            "name": track.name,
            "id": i,
            "events": [],
            "notes": []
        }
        active_notes = {}
        absolute_time = 0
        ticks_since_last_note_on = 0

        for msg in track:
            # if msg.type == 'text':
            #     print(f'{track.name=} {msg.text=} {msg.time=}')

            # On any event, the absolute time is still increasing.
            absolute_time += msg.time
            ticks_since_last_note_on += msg.time

            if msg.type == 'text':
                event_text = msg.text

                # Tempo of note
                tempo_event = get_tempo(absolute_time, tempo_times)
                event_bpm = tempo_event[1]
                absolute_time_of_event = tempo_event[0]
                time_event_began = tempo_event[2]
                ticks_for_recalc = absolute_time - absolute_time_of_event

                current_event_time_s = time_event_began + get_length_in_beats(event_bpm, ticks_for_recalc, mid.ticks_per_beat)
                track_data['events'].append({
                    'time': current_event_time_s * 1000,
                    'text': event_text
                })

            # If a note starts playing, write it down
            if msg.type == 'note_on':
                # Get the time in beats and increment the value

                # Tempo of note
                tempo_event = get_tempo(absolute_time, tempo_times)
                event_bpm = tempo_event[1]

                absolute_time_of_event = tempo_event[0]

                time_event_began = tempo_event[2]
                
                ticks_for_recalc = absolute_time - absolute_time_of_event

                if ticks_for_recalc < 0:
                    print("WARNING NOTE USES PREVIOUS BPM CHANGE")
                #ticks_for_recalc = 0

                current_note_time_s = time_event_began + get_length_in_beats(event_bpm, ticks_for_recalc, mid.ticks_per_beat)

                #print(f'\n\n\n\n\n\nTempo at note_on: {bpm_note}\nTime: {current_note_time_s}\nNote Key: {msg.note}\nAbsolute time of event: {absolute_time_of_event}\nAbs time: {absolute_time}\nDiff: {ticks_for_recalc}\nTime ms of event: {time_at_change}\nTime beats: {get_length_in_beats(bpm_note, ticks_for_recalc + ticks_since_last_note_on, mid.ticks_per_beat)}')

                # Use the current ticks_since_last_note_on, where we know at which tick began since the last note_on event
                # Because the  time ticks_since_last_note_on is still increasing, note_off events will not affect this.
                active_notes[msg.note] = [
                    ticks_since_last_note_on,
                    current_note_time_s,
                    absolute_time,
                ]

                # Reset the ticks_since_last_note_on
                ticks_since_last_note_on = 0

                #time.sleep(0.1)
                
            elif msg.type == 'note_off':
                # Get the note_on event
                note_on_event = active_notes.pop(msg.note, None)

                if note_on_event is not None:
                    # Get the ticks since last note_on event at which this note began.
                    note_ticks_since_last = note_on_event[0]

                    # The time in beats this note began at
                    note_time = note_on_event[1]

                    # The absolute time the note began
                    absolute_time_note_began = note_on_event[2]

                    # When this note_off event starts, the duration will be the ticks since the last event
                    # (last event being note_on)
                    note_duration_ticks = absolute_time - absolute_time_note_began

                    tempo_event = get_tempo(absolute_time, tempo_times)
                    bpm_note = tempo_event[1]
                    #print(f'Tempo at note_on: {bpm_note}')

                    note_duration = get_length_in_beats(bpm_note, note_duration_ticks, mid.ticks_per_beat)

                    # A hold note will be longer than a step.
                    is_hold_note = note_duration_ticks > int(mid.ticks_per_beat / 4)

                    #print(int(mid.ticks_per_beat / 4))
                    
                    note_data = {
                        'note': msg.note,

                        # 'ticks_since_last': note_ticks_since_last,
                        # 'ticks_duration': note_duration_ticks,

                        # 'absolute_time_of_note': absolute_time,

                        # 'tempo_note': bpm_note,

                        # Compat values
                        'is_hold_note': is_hold_note,
                        'start_time': note_time * 1000,
                        'duration': note_duration * 1000
                        
                        # 'descriptor': dascription
                    }

                    track_data['notes'].append(note_data)
                    
        midi_data['tracks'].append(track_data)

    # events = parse_text_events(midi_file_path)
    # for track_events in events:
    #     if track_events:  # Check if track_events is not empty
    #         track_name = track_events[0][2]  # First event's text is assumed to be the track name
    #         track_data = next((track for track in midi_data['tracks'] if track['name'] == track_name), None)
    #         if track_data is None:
    #             track_data = {"name": track_name, "events": []}
    #             midi_data['tracks'].append(track_data)

    #         for delta_time, event_type, event_text in track_events:
    #             print(f'{event_text=} {delta_time=}')

    #             track_data['events'].append({
    #                 "time": delta_time,  # Convert ticks to seconds
    #                 "event_type": event_type,
    #                 'description': 'TEMPO CHANGE' if event_type == 81 else 'TIME SIGNATURE' if event_type == 88 else 'TRACK NAME' if event_text == track_name else 'TEXT',
    #                 "event_text": event_text
    #             })

    return midi_data

# def parse_text_events(midi_file_path):
#     events = []
#     with open(midi_file_path, 'rb') as midi_file:
#         header_chunk = midi_file.read(14)
#         track_header = midi_file.read(8)
#         while track_header:
#             track_id = int.from_bytes(track_header[0:4], byteorder='big')
#             track_length = int.from_bytes(track_header[4:8], byteorder='big')
#             track_data = midi_file.read(track_length)
#             events.append(parse_track(track_data))
#             track_header = midi_file.read(8)
#     return events

# def parse_track(track_data):
#     events = []
#     idx = 0
#     while idx < len(track_data):
#         delta_time, idx = read_variable_length(track_data, idx)
#         if idx >= len(track_data):
#             break  # Break out of loop if no more data to parse
#         event_type = track_data[idx]
#         idx += 1
#         if event_type == 0xFF:  # Meta Event
#             if idx + 1 >= len(track_data):
#                 break  # Break out of loop if no more data to parse
#             meta_event_type = track_data[idx]
#             idx += 1
#             if idx >= len(track_data):
#                 break  # Break out of loop if no more data to parse
#             meta_length, idx = read_signed_variable_length(track_data, idx)
#             if idx + meta_length > len(track_data):
#                 break  # Break out of loop if meta data exceeds available data
#             meta_data = track_data[idx:idx + meta_length]
#             idx += meta_length
#             value = None
#             if meta_event_type in [81, 88]:  # Tempo or Time Signature Event
#                 value = int.from_bytes(meta_data, byteorder='big')
#             else:
#                 value = try_decode(meta_data)
#             events.append((delta_time, meta_event_type, value))
#         else:
#             # Handle other MIDI events if necessary
#             pass
#     return events

# def try_decode(data):
#     encodings = ['utf-8', 'latin-1', 'iso-8859-1']
#     for encoding in encodings:
#         try:
#             return data.decode(encoding)
#         except UnicodeDecodeError:
#             pass
#     return None

# def read_variable_length(data, idx):
#     value = 0
#     while True:
#         byte = data[idx]
#         idx += 1
#         value = (value << 7) | (byte & 0x7F)  # Use bitwise OR for clarity
#         if not byte & 0x80:
#             break
#     return value, idx

# def read_signed_variable_length(data, idx):
#   value = 0
#   is_negative = False
#   while True:
#     byte = data[idx]
#     idx += 1
#     is_negative = is_negative or (byte & 0x80)  # Check for sign bit
#     value = (value << 7) | (byte & 0x7F)
#     if not byte & 0x80:
#       break
#   # Apply sign extension if necessary
#   if is_negative:
#     value = value - (1 << (len(data) - idx))  # Two's complement extension
#   return value, idx

if __name__ == '__main__':
    thing = midi_to_object('notes.mid')
    open('notes_test.json', 'w').write(json.dumps(thing, indent=4))

# descriptions = {
#     60: 'One E',
#     61: 'Two E',
#     62: 'Thr E',
#     63: 'Fou E',
#     64: 'Fiv E',
#     66: 'One E Lift',
#     67: 'Two E Lift',
#     68: 'Thr E Lift',
#     69: 'Fou E Lift',
#     70: 'Fiv E Lift',
#     72: 'One N',
#     73: 'Two N',
#     74: 'Thr N',
#     75: 'Fou N',
#     76: 'Fiv N',
#     78: 'One N Lift',
#     79: 'Two N Lift',
#     80: 'Thr N Lift',
#     81: 'Fou N Lift',
#     82: 'Fiv N Lift',
#     84: 'One H',
#     85: 'Two H',
#     86: 'Thr H',
#     87: 'Fou H',
#     88: 'Fiv H',
#     90: 'One H Lift',
#     91: 'Two H Lift',
#     92: 'Thr H Lift',
#     93: 'Fou H Lift',
#     94: 'Fiv H Lift',
#     96: 'One X',
#     97: 'Two X',
#     98: 'Thr X',
#     99: 'Fou X',
#     100: 'Fiv X',
#     102: 'One X Lift',
#     103: 'Two X Lift',
#     104: 'Thr X Lift',
#     105: 'Fou X Lift',
#     106: 'Fiv X Lift',
# }