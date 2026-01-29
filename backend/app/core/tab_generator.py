import numpy as np
import librosa

class TabGenerator:
    
    def __init__(self, tuning=None):
        if tuning is None:
            tuning = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
        self.tuning = tuning
        self.tuning_freqs = [self.note_to_frequency(note) for note in tuning]
        self.tuning_midi = [librosa.note_to_midi(note) for note in tuning]
    
    def note_to_frequency(self, note_name):
        A4 = 440.0
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        note = note_name[:-1]
        octave = int(note_name[-1])
        
        semitone = notes.index(note)
        n = (octave - 4) * 12 + semitone - 9
        
        return A4 * (2 ** (n / 12))
    
    def frequency_to_note(self, freq):
        if freq <= 0:
            return None, None
        
        A4 = 440.0
        C0 = A4 * pow(2, -4.75)
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        h = round(12 * np.log2(freq / C0))
        octave = h // 12
        n = h % 12
        
        return note_names[n], octave
    
    def find_all_positions_for_note(self, midi_note, max_fret=12):
        """
        Find ALL possible positions for a MIDI note (limited to practical frets)
        
        Args:
            midi_note: MIDI note number
            max_fret: Maximum fret to consider (default 12 for open chords)
            
        Returns:
            list: All possible positions
        """
        positions = []
        
        for string_idx, string_midi in enumerate(self.tuning_midi):
            fret = midi_note - string_midi
            
            if 0 <= fret <= max_fret:
                positions.append({
                    'string': 6 - string_idx,
                    'fret': fret,
                    'midi_note': midi_note,
                    'string_idx': string_idx
                })
        
        return positions
    
    def score_chord_shape(self, chord_positions, chord_midi_notes):
        """
        Score a complete chord shape based on playability
        
        Args:
            chord_positions: List of positions (one per note)
            chord_midi_notes: List of MIDI notes (MUST be sorted from low to high)
            
        Returns:
            float: Score (higher = better)
        """
        if not chord_positions:
            return -1000
        
        score = 0
        frets = [p['fret'] for p in chord_positions]
        strings = [p['string'] for p in chord_positions]
        
        # CRITIQUE: Pénalité si deux notes sur la même corde (impossible physiquement)
        if len(strings) != len(set(strings)):
            return -100000
        
        # CRITIQUE: Créer une map note MIDI → string pour vérifier l'ordre
        midi_to_string = {midi: pos['string'] for midi, pos in zip(chord_midi_notes, chord_positions)}
        
        # Trier les notes MIDI du grave à l'aigu
        sorted_midi = sorted(chord_midi_notes)
        
        # Les strings correspondantes doivent être en ordre DÉCROISSANT
        # Exemple: [C3, E3, G3, C4, E4] → strings [5, 4, 3, 2, 1]
        prev_string = 7  # Commence à 7 (plus que le max qui est 6)
        for midi in sorted_midi:
            current_string = midi_to_string[midi]
            
            # La corde doit être STRICTEMENT plus petite (plus aiguë) que la précédente
            if current_string >= prev_string:
                # Ordre incorrect ! Note plus aiguë sur corde plus grave
                return -100000
            
            prev_string = current_string
        
        # BONUS: Respecte l'ordre logique
        score += 100
        
        # Vérifier ranges logiques par note
        for i, (pos, midi) in enumerate(zip(chord_positions, chord_midi_notes)):
            # Notes très graves (< E3 = MIDI 52) devraient être sur cordes 4-6
            if midi < 52:
                if pos['string'] >= 4:
                    score += 50  # Bonus
                else:
                    score -= 500  # Pénalité
            
            # Notes moyennes (E3 à C4) sur cordes 2-4
            elif 52 <= midi <= 60:
                if 2 <= pos['string'] <= 4:
                    score += 30
            
            # Notes aiguës (> C4) sur cordes 1-3
            else:
                if pos['string'] <= 3:
                    score += 50
                else:
                    score -= 500
        
        # 1. Pénalité pour frettes hautes
        for fret in frets:
            if fret > 5:
                score -= (fret ** 2.5)
            else:
                score -= (fret ** 1.2)
        
        # 2. BONUS ÉNORME pour cordes à vide
        open_strings = sum(1 for f in frets if f == 0)
        score += open_strings * 200
        
        # 3. BONUS pour frettes 1-3
        for fret in frets:
            if 1 <= fret <= 3:
                score += 80
        
        # 4. Pénalité pour écart entre frettes
        non_zero_frets = [f for f in frets if f > 0]
        if len(non_zero_frets) >= 2:
            fret_span = max(non_zero_frets) - min(non_zero_frets)
            if fret_span > 4:
                score -= (fret_span ** 2) * 50
            elif fret_span <= 3:
                score += 30
        
        # 5. BONUS pour cohérence
        if len(non_zero_frets) >= 2:
            avg_fret = np.mean(non_zero_frets)
            for fret in non_zero_frets:
                distance = abs(fret - avg_fret)
                if distance <= 2:
                    score += 25
                else:
                    score -= distance * 15
        
        return score
    
    def find_best_chord_positions(self, chord_notes, max_fret=12, debug=False):
        """
        Find the best positions for all notes in a chord simultaneously
        
        Args:
            chord_notes: List of MIDI note numbers in the chord
            max_fret: Maximum fret to consider
            debug: Print detailed scoring info
            
        Returns:
            list: Best positions for each note
        """
        # ÉTAPE 1: Trier les notes (grave → aigu)
        sorted_notes = sorted(chord_notes)
        
        # ÉTAPE 2: Pour chaque note, trouver TOUTES les positions possibles
        all_possibilities = []
        for note in sorted_notes:
            positions = self.find_all_positions_for_note(note, max_fret)
            if not positions:
                print(f"  ⚠️ Aucune position trouvée pour MIDI {note}")
                return []
            
            # TRI IMPORTANT: Positions par ordre de préférence
            # Priorité: corde à vide > frette 1-3 > autres
            positions.sort(key=lambda p: (
                -1 if p['fret'] == 0 else (0 if p['fret'] <= 3 else 1),  # Catégorie
                p['fret']  # Puis par numéro de frette
            ))
            
            all_possibilities.append(positions)
            
            if debug:
                print(f"  Note MIDI {note}: {len(positions)} positions trouvées")
                for i, p in enumerate(positions[:3]):
                    print(f"    {i+1}. String {p['string']}, Fret {p['fret']}")
        
        # ÉTAPE 3: Limiter les combinaisons pour éviter l'explosion
        # Garder maximum 4 positions par note (priorisées ci-dessus)
        all_possibilities = [p[:4] for p in all_possibilities]
        
        # ÉTAPE 4: Évaluer TOUTES les combinaisons
        from itertools import product
        
        best_score = -float('inf')
        best_combination = None
        
        evaluated = 0
        for combination in product(*all_possibilities):
            combination_list = list(combination)
            score = self.score_chord_shape(combination_list, sorted_notes)  # Passer les MIDI notes
            
            evaluated += 1
            
            if score > best_score:
                best_score = score
                best_combination = combination_list
                
                if debug and score > 0:
                    print(f"  ✨ Nouvelle meilleure combinaison (score: {score:.0f}):")
                    for pos in combination_list:
                        print(f"     String {pos['string']}, Fret {pos['fret']}")
        
        print(f"  → Évalué {evaluated} combinaisons, meilleur score: {best_score:.0f}")
        
        return best_combination if best_combination else []
    
    def group_into_chords(self, midi_notes, chord_window=0.5):
        """
        Group MIDI notes into chords based on timing
        
        Args:
            midi_notes: List of note dictionaries
            chord_window: Time window to consider notes simultaneous (seconds)
            
        Returns:
            list: List of chord groups
        """
        if not midi_notes:
            return []
        
        # Sort by start time
        sorted_notes = sorted(midi_notes, key=lambda x: x['start_time'])
        
        chords = []
        current_chord = [sorted_notes[0]]
        
        for note in sorted_notes[1:]:
            # Check if note starts within chord_window of first note
            if note['start_time'] - current_chord[0]['start_time'] <= chord_window:
                current_chord.append(note)
            else:
                chords.append(current_chord)
                current_chord = [note]
        
        # Add last chord
        if current_chord:
            chords.append(current_chord)
        
        return chords
    
    def generate_tab_from_midi_notes(self, midi_notes, min_duration=0.1, chord_window=0.5, max_fret=12, max_gap=1.0):
        """
        Generate tablature from MIDI notes using chord-aware positioning
        
        Args:
            midi_notes: List of note dictionaries from AudioTranscriber
            min_duration: Minimum note duration to include (seconds)
            chord_window: Time window to group notes as chord (seconds)
            max_fret: Maximum fret to consider
            max_gap: Maximum silence gap - stop after this (seconds). Set to None to process all.
            
        Returns:
            list: Tablature data with positions
        """
        # Filter short notes
        filtered_notes = [n for n in midi_notes if n['duration'] >= min_duration]
        
        # Group into chords
        chords = self.group_into_chords(filtered_notes, chord_window)
        
        print(f"  📋 {len(chords)} accord(s) détecté(s) avant filtrage")
        
        # NOUVEAU: Détecter les silences longs et couper après le premier accord principal
        if max_gap is not None and len(chords) > 1:
            # Vérifier le gap temporel entre le DÉBUT du premier et deuxième accord
            # (plus fiable que la fin de la dernière note qui peut résonner longtemps)
            gap = chords[1][0]['start_time'] - chords[0][0]['start_time']
            print(f"  ⏱️ Temps entre accord 1 et 2: {gap:.2f}s (seuil: {max_gap}s)")
            if gap > max_gap:
                print(f"  ⏸️ Grand écart temporel détecté - traitement du premier accord uniquement")
                chords = chords[:1]
            else:
                print(f"  ✓ Écart trop court, conservation de tous les accords")
        
        print(f"  📋 {len(chords)} accord(s) après filtrage")
        
        tab_data = []
        
        for chord_idx, chord in enumerate(chords):
            print(f"\n🎵 Traitement accord #{chord_idx + 1}:")
            
            # IMPORTANT: Supprimer les doublons (même note MIDI détectée plusieurs fois)
            unique_notes = {}
            for note in chord:
                midi_num = note['midi_note']
                # Garder la note avec la plus haute vélocité (la plus forte)
                if midi_num not in unique_notes or note['velocity'] > unique_notes[midi_num]['velocity']:
                    unique_notes[midi_num] = note
            
            unique_chord = list(unique_notes.values())
            
            if len(unique_chord) < len(chord):
                print(f"  ⚠️ Doublons supprimés: {len(chord)} → {len(unique_chord)} notes uniques")
                print(f"  Notes: {[n['note_name'] for n in unique_chord]}")
            
            # Extract MIDI notes
            chord_midi_notes = [n['midi_note'] for n in unique_chord]
            
            # Find best positions for this chord as a whole
            positions = self.find_best_chord_positions(chord_midi_notes, max_fret)
            
            if not positions:
                print(f"  ❌ Impossible de trouver des positions pour cet accord")
                continue
            
            # Create tab data for each note with its position
            for note, pos in zip(unique_chord, positions):
                tab_data.append({
                    'start_time': note['start_time'],
                    'end_time': note['end_time'],
                    'duration': note['duration'],
                    'midi_note': note['midi_note'],
                    'frequency': note['frequency'],
                    'note_name': note['note_name'],
                    'string': pos['string'],
                    'fret': pos['fret'],
                    'velocity': note['velocity']
                })
        
        return sorted(tab_data, key=lambda x: x['start_time'])
    
    def format_tab_ascii(self, tab_data, duration=None, time_scale=1.0):
        """
        Format tab data as ASCII tablature
        
        Args:
            tab_data: List of note dictionaries
            duration: Total duration (optional)
            time_scale: Scale factor for horizontal spacing
            
        Returns:
            str: ASCII tablature
        """
        if not tab_data:
            return "No notes detected"

        # Initialize lines
        lines = {1: 'e|', 2: 'B|', 3: 'G|', 4: 'D|', 5: 'A|', 6: 'E|'}
        
        # Sort by time
        sorted_data = sorted(tab_data, key=lambda x: x.get('start_time', x.get('time', 0)))
        
        # Build tablature
        for note in sorted_data:
            string_num = note['string']
            fret = note['fret']
            fret_str = str(fret)
            
            max_width = len(fret_str)
            
            for s in range(1, 7):
                if s == string_num:
                    lines[s] += fret_str + '-'
                else:
                    lines[s] += '-' * (max_width + 1)
        
        # Add ending
        for s in range(1, 7):
            lines[s] += '|'
        
        return '\n'.join([lines[1], lines[2], lines[3], lines[4], lines[5], lines[6]])


def test_tab_generator_with_midi():
    """Test with MIDI notes from basic-pitch"""
    import sys
    import os
    sys.path.append('..')
    from transcriber import AudioTranscriber
    
    generator = TabGenerator()
    transcriber = AudioTranscriber()
    
    print("=" * 60)
    print("Testing Tab Generator with Chord-Aware Logic")
    print("=" * 60)
    print()
    
    # Transcribe audio
    audio_file = "tests/315706__spitefuloctopus__acousticguitar-c-chord.wav"
    result = transcriber.transcribe_audio(audio_file)
    
    # Generate tabs with chord awareness
    tab_data = generator.generate_tab_from_midi_notes(
        result['notes'], 
        min_duration=0.1,
        chord_window=0.6,
        max_fret=12,  # Only consider first 12 frets for open chords
        max_gap=1.0   # Stop after 1 second silence (keep only first chord)
    )
    
    print(f"📊 Generated {len(tab_data)} tab positions")
    print()
    
    # Show detected positions
    print("Detected Tab Positions:")
    print("-" * 60)
    for i, note in enumerate(tab_data[:10]):
        print(f"{i+1:2d}. Time: {note['start_time']:.3f}s | "
              f"Note: {note['note_name']:4s} | "
              f"String: {note['string']} | "
              f"Fret: {note['fret']:2d}")
    
    print()
    print("Generated ASCII Tablature:")
    print("-" * 60)
    print(generator.format_tab_ascii(tab_data))
    print()
    
    # Show chord analysis
    chords = generator.group_into_chords(result['notes'], chord_window=0.6)
    print(f"🎵 Detected {len(chords)} chord group(s)")
    
    if chords:
        print("\nFirst Chord Analysis:")
        print("-" * 60)
        
        # Supprimer les doublons pour l'analyse aussi
        first_chord = chords[0]
        unique_notes_dict = {}
        for note in first_chord:
            midi_num = note['midi_note']
            if midi_num not in unique_notes_dict or note['velocity'] > unique_notes_dict[midi_num]['velocity']:
                unique_notes_dict[midi_num] = note
        
        unique_first_chord = list(unique_notes_dict.values())
        chord_notes = [n['note_name'] for n in unique_first_chord]
        print(f"Notes (uniques): {', '.join(chord_notes)}")
        
        # Find positions for first chord
        first_chord_midi = [n['midi_note'] for n in unique_first_chord]
        positions = generator.find_best_chord_positions(first_chord_midi, max_fret=12)
        
        print("\nChosen positions:")
        for i, pos in enumerate(positions):
            print(f"  {chord_notes[i]:4s} (MIDI {first_chord_midi[i]:2d}) → String {pos['string']}, Fret {pos['fret']}")
    
    print()
    print("=" * 60)
    print("✅ Test completed!")


if __name__ == "__main__":
    test_tab_generator_with_midi()