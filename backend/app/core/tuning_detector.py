"""
Guitar tuning detection module
Analyzes detected notes to determine the most likely guitar tuning
Supports capo detection (positions 1-7)
"""

import numpy as np
import librosa
from collections import Counter


class TuningDetector:
    """
    Detects guitar tuning from transcribed notes
    """
    
    # Common guitar tunings (from low to high string)
    COMMON_TUNINGS = {
        'standard': ['E2', 'A2', 'D3', 'G3', 'B3', 'E4'],
        'drop_d': ['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],
        'drop_c': ['C2', 'G2', 'C3', 'F3', 'A3', 'D4'],
        'drop_c#': ['C#2', 'G#2', 'C#3', 'F#3', 'A#3', 'D#4'],
        'drop_b': ['B1', 'F#2', 'B2', 'E3', 'G#3', 'C#4'],
        'eb_standard': ['Eb2', 'Ab2', 'Db3', 'Gb3', 'Bb3', 'Eb4'],
        'd_standard': ['D2', 'G2', 'C3', 'F3', 'A3', 'D4'],
        'open_d': ['D2', 'A2', 'D3', 'F#3', 'A3', 'D4'],
        'open_g': ['D2', 'G2', 'D3', 'G3', 'B3', 'D4'],
        'dadgad': ['D2', 'A2', 'D3', 'G3', 'A3', 'D4'],
    }
    
    def __init__(self):
        # Convertir les tunings en MIDI pour comparaison
        self.tunings_midi = {}
        for name, tuning in self.COMMON_TUNINGS.items():
            self.tunings_midi[name] = [librosa.note_to_midi(note) for note in tuning]
    
    def detect_tuning(self, midi_notes, confidence_threshold=0.6):
        """
        Detect the most likely guitar tuning from detected notes.
        Also detects if a capo is used and at which fret.
        
        Args:
            midi_notes: List of note dictionaries from AudioTranscriber
            confidence_threshold: Minimum confidence to return a result
            
        Returns:
            dict: {
                'detected_tuning': str,
                'confidence': float,
                'tuning_notes': list,
                'capo': int,           # 0 = no capo, 1-7 = capo fret
                'capo_label': str,     # Human-readable capo info
                'analysis': dict
            }
        """
        if not midi_notes:
            return {
                'detected_tuning': 'unknown',
                'confidence': 0.0,
                'tuning_notes': [],
                'capo': 0,
                'capo_label': 'No capo',
                'analysis': {'error': 'No notes detected'}
            }
        
        # Extraire les notes MIDI uniques
        unique_midi = list(set([note['midi_note'] for note in midi_notes]))
        
        # Analyser les notes graves (6 plus graves)
        sorted_notes = sorted(unique_midi)
        low_notes = sorted_notes[:min(6, len(sorted_notes))]
        
        # Compter la fréquence de chaque note (pour détecter les cordes à vide)
        note_counts = Counter([n['midi_note'] for n in midi_notes])
        
        # --- ÉTAPE 1 : Trouver le meilleur tuning sans capo ---
        scores = {}
        for tuning_name, tuning_midi in self.tunings_midi.items():
            score = self._score_tuning(tuning_midi, unique_midi, low_notes, note_counts)
            scores[tuning_name] = score
        
        best_tuning = max(scores, key=scores.get)
        best_score = scores[best_tuning]
        
        # --- ÉTAPE 2 : Tester le même tuning avec capo 1-7 ---
        best_capo = 0
        best_capo_score = best_score

        # Seuil : le score avec capo doit être significativement meilleur
        # pour éviter les faux positifs
        CAPO_IMPROVEMENT_THRESHOLD = 15

        for capo_fret in range(1, 8):
            transposed_midi = [m + capo_fret for m in self.tunings_midi[best_tuning]]
            capo_score = self._score_tuning(transposed_midi, unique_midi, low_notes, note_counts)
            
            if capo_score > best_capo_score + CAPO_IMPROVEMENT_THRESHOLD:
                best_capo_score = capo_score
                best_capo = capo_fret

        # Utiliser le score final (avec ou sans capo)
        final_score = best_capo_score if best_capo > 0 else best_score
        
        # Normaliser le score (0-1)
        confidence = min(1.0, final_score / 100.0)
        
        # Label lisible pour le capo
        ordinals = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th', 7: '7th'}
        capo_label = f"Capo {ordinals[best_capo]} fret" if best_capo > 0 else "No capo"

        # Préparer l'analyse détaillée
        analysis = {
            'detected_notes': [librosa.midi_to_note(m) for m in sorted_notes],
            'low_notes': [librosa.midi_to_note(m) for m in low_notes],
            'all_scores': {name: round(score, 2) for name, score in sorted(scores.items(), key=lambda x: -x[1])[:5]},
            'note_count': len(unique_midi),
            'most_frequent_notes': [
                (librosa.midi_to_note(midi), count) 
                for midi, count in note_counts.most_common(10)
            ]
        }
        
        result = {
            'detected_tuning': best_tuning,
            'confidence': round(confidence, 3),
            'tuning_notes': self.COMMON_TUNINGS[best_tuning],
            'capo': best_capo,
            'capo_label': capo_label,
            'analysis': analysis
        }
        
        # Si la confiance est trop faible, marquer comme incertain
        if confidence < confidence_threshold:
            result['detected_tuning'] = f"{best_tuning} (low confidence)"
            result['warning'] = f"Confidence {confidence:.1%} is below threshold {confidence_threshold:.1%}"
        
        return result
    
    def _score_tuning(self, tuning_midi, detected_midi, low_notes, note_counts):
        """
        Score how well a tuning matches the detected notes
        
        Args:
            tuning_midi: MIDI notes of the tuning (already transposed if capo)
            detected_midi: All detected MIDI notes
            low_notes: Lowest detected notes
            note_counts: Frequency of each note
            
        Returns:
            float: Score (higher = better match)
        """
        score = 0
        
        # 1. Les cordes à vide du tuning devraient être présentes et fréquentes
        for tuning_note in tuning_midi:
            if tuning_note in detected_midi:
                score += 20  # Note présente
                
                # Bonus si c'est une note fréquente (probablement corde à vide)
                frequency = note_counts.get(tuning_note, 0)
                if frequency > 2:
                    score += min(frequency * 5, 30)  # Max +30 pour notes très fréquentes
        
        # 2. La note la plus grave détectée devrait matcher la corde grave du tuning
        if low_notes:
            lowest_detected = low_notes[0]
            lowest_tuning = tuning_midi[0]
            
            # Match parfait
            if lowest_detected == lowest_tuning:
                score += 40
            # Proche (± 1 semitone)
            elif abs(lowest_detected - lowest_tuning) == 1:
                score += 20
            # Octave
            elif abs(lowest_detected - lowest_tuning) == 12:
                score += 15
            # Trop différent
            elif abs(lowest_detected - lowest_tuning) > 3:
                score -= 20
        
        # 3. Les notes détectées devraient être jouables dans ce tuning
        # (sur le manche jusqu'à la 12ème frette)
        playable_notes = set()
        for string_midi in tuning_midi:
            for fret in range(13):  # 0-12 frettes
                playable_notes.add(string_midi + fret)
        
        # Bonus pour notes jouables
        for detected in detected_midi:
            if detected in playable_notes:
                score += 2
            else:
                score -= 5  # Pénalité pour notes non jouables
        
        return score
    
    def get_tuning_info(self, tuning_name):
        """
        Get detailed information about a specific tuning
        
        Args:
            tuning_name: Name of the tuning
            
        Returns:
            dict: Tuning information
        """
        if tuning_name not in self.COMMON_TUNINGS:
            return None
        
        tuning = self.COMMON_TUNINGS[tuning_name]
        
        return {
            'name': tuning_name,
            'display_name': tuning_name.replace('_', ' ').title(),
            'notes': tuning,
            'midi_notes': self.tunings_midi[tuning_name],
            'frequencies': [librosa.note_to_hz(note) for note in tuning]
        }
    
    def list_all_tunings(self):
        """
        Get list of all supported tunings
        
        Returns:
            list: List of tuning information
        """
        return [self.get_tuning_info(name) for name in self.COMMON_TUNINGS.keys()]


def test_tuning_detector():
    """
    Test the tuning detector with sample data
    """
    from transcriber import AudioTranscriber
    import os
    
    print("=" * 60)
    print("Testing Tuning Detector")
    print("=" * 60)
    print()
    
    audio_file = "tests/315706__spitefuloctopus__acousticguitar-c-chord.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ Test file not found: {audio_file}")
        return
    
    transcriber = AudioTranscriber()
    print("🎵 Transcribing audio...")
    result = transcriber.transcribe_audio(audio_file)
    
    detector = TuningDetector()
    print("\n🎸 Detecting tuning...")
    tuning_result = detector.detect_tuning(result['notes'])
    
    print("\n📊 Results:")
    print("-" * 60)
    print(f"Detected Tuning: {tuning_result['detected_tuning']}")
    print(f"Confidence: {tuning_result['confidence']:.1%}")
    print(f"Tuning Notes: {' - '.join(tuning_result['tuning_notes'])}")
    print(f"Capo: {tuning_result['capo_label']}")
    
    if 'warning' in tuning_result:
        print(f"\n⚠️  {tuning_result['warning']}")
    
    print("\n📋 Analysis:")
    print(f"  Total unique notes: {tuning_result['analysis']['note_count']}")
    print(f"  Low notes detected: {', '.join(tuning_result['analysis']['low_notes'])}")
    print(f"\n  Top 5 tuning matches:")
    for tuning, score in list(tuning_result['analysis']['all_scores'].items())[:5]:
        print(f"    {tuning:15s}: {score:.1f}")
    
    print(f"\n  Most frequent notes:")
    for note, count in tuning_result['analysis']['most_frequent_notes'][:5]:
        print(f"    {note:4s}: {count} times")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")


if __name__ == "__main__":
    test_tuning_detector()