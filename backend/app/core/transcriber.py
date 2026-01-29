"""
Audio transcription module using basic-pitch (Spotify's model)
Converts audio files to MIDI notes with timing information
"""

import numpy as np
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import librosa


class AudioTranscriber:
    """
    Handles audio transcription using basic-pitch
    """
    
    def __init__(self, model_path=ICASSP_2022_MODEL_PATH):
        """
        Initialize the transcriber
        
        Args:
            model_path: Path to the basic-pitch model (uses default if None)
        """
        self.model_path = model_path
    
    def transcribe_audio(self, audio_path, onset_threshold=0.5, frame_threshold=0.3):
        """
        Transcribe audio file to MIDI notes
        
        Args:
            audio_path: Path to the audio file
            onset_threshold: Threshold for note onset detection (0-1)
            frame_threshold: Threshold for note frame detection (0-1)
            
        Returns:
            dict: {
                'notes': list of detected notes with timing,
                'sample_rate': audio sample rate,
                'duration': audio duration in seconds
            }
        """
        print(f"🎵 Transcribing audio: {audio_path}")
        
        
        model_output, midi_data, note_events = predict(
            audio_path,
            self.model_path,
            onset_threshold=onset_threshold,
            frame_threshold=frame_threshold,
            minimum_note_length=127.70,  
            minimum_frequency=None,  
            maximum_frequency=None,  
            multiple_pitch_bends=False,
            melodia_trick=True,
            debug_file=None
        )
        
        
        audio, sr = librosa.load(audio_path, sr=None)
        duration = len(audio) / sr
        
        
        notes = self._extract_notes_from_midi(midi_data, note_events)
        
        print(f"✅ Transcription complete: {len(notes)} notes detected")
        
        return {
            'notes': notes,
            'sample_rate': sr,
            'duration': duration,
            'midi_data': midi_data 
        }
    
    def _extract_notes_from_midi(self, midi_data, note_events):
        """
        Extract note information from MIDI data
        
        Args:
            midi_data: pretty_midi.PrettyMIDI object
            note_events: List of note events from basic-pitch
            
        Returns:
            list: List of note dictionaries with timing and pitch info
        """
        notes = []
        
        
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                notes.append({
                    'start_time': float(note.start),
                    'end_time': float(note.end),
                    'duration': float(note.end - note.start),
                    'midi_note': int(note.pitch),
                    'frequency': self.midi_to_frequency(note.pitch),
                    'velocity': int(note.velocity),
                    'note_name': librosa.midi_to_note(note.pitch)
                })
        
        
        notes.sort(key=lambda x: x['start_time'])
        
        return notes
    
    @staticmethod
    def midi_to_frequency(midi_note):
        """
        Convert MIDI note number to frequency in Hz
        
        Args:
            midi_note: MIDI note number (0-127)
            
        Returns:
            float: Frequency in Hz
        """
        
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
    
    @staticmethod
    def frequency_to_midi(frequency):
        """
        Convert frequency to MIDI note number
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            int: MIDI note number
        """
        if frequency <= 0:
            return None
        return int(round(69 + 12 * np.log2(frequency / 440.0)))


def test_transcriber():
    """
    Test the transcriber with a sample audio file
    """
    import os
    
    
    audio_file = "tests/315706__spitefuloctopus__acousticguitar-c-chord.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ Test file not found: {audio_file}")
        return
    
    print("=" * 60)
    print("Testing Audio Transcriber with basic-pitch")
    print("=" * 60)
    print()
    
    
    transcriber = AudioTranscriber()
    
    
    result = transcriber.transcribe_audio(audio_file)
    
    print()
    print("📊 Transcription Results:")
    print("-" * 60)
    print(f"Duration: {result['duration']:.2f} seconds")
    print(f"Sample rate: {result['sample_rate']} Hz")
    print(f"Total notes detected: {len(result['notes'])}")
    print()
    
    
    print("Detected Notes:")
    print("-" * 60)
    
    for i, note in enumerate(result['notes'][:20]):  
        print(f"{i+1:2d}. Time: {note['start_time']:.3f}s - {note['end_time']:.3f}s "
              f"({note['duration']:.3f}s) | "
              f"Note: {note['note_name']:4s} | "
              f"MIDI: {note['midi_note']:3d} | "
              f"Freq: {note['frequency']:7.2f} Hz | "
              f"Vel: {note['velocity']:3d}")
    
    if len(result['notes']) > 20:
        print(f"... and {len(result['notes'] - 20)} more notes")
    
    print()
    print("=" * 60)
    print("✅ Test completed!")
    print()


if __name__ == "__main__":
    test_transcriber()