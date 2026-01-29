"""
Test script for audio transcription using crepe
"""

import crepe
import numpy as np
from scipy.io import wavfile
import os

def test_audio_transcription(audio_path):
    """
    Test audio transcription with crepe
    
    Args:
        audio_path: Path to the audio file
    """
    print(f"🎸 Testing audio file: {audio_path}")
    print("-" * 50)
    
    
    if not os.path.exists(audio_path):
        print(f"❌ Error: File not found at {audio_path}")
        return
    
    
    print("📂 Loading audio file...")
    sr, audio = wavfile.read(audio_path)
    
    
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    
    
    audio = audio.astype(float)
    if audio.max() > 0:
        audio = audio / np.abs(audio).max()
    
    print(f"✅ Audio loaded successfully!")
    print(f"   Sample rate: {sr} Hz")
    print(f"   Duration: {len(audio) / sr:.2f} seconds")
    print(f"   Samples: {len(audio)}")
    print()
    
    
    print("🎵 Analyzing audio with crepe...")
    time, frequency, confidence, activation = crepe.predict(
        audio, 
        sr, 
        viterbi=True,
        model_capacity='medium'
    )
    
    print(f"✅ Analysis complete!")
    print()
    
    
    print("📊 Detection Results:")
    print("-" * 50)
    
    
    confident_indices = confidence > 0.5
    
    if confident_indices.any():
        confident_times = time[confident_indices]
        confident_freqs = frequency[confident_indices]
        confident_confs = confidence[confident_indices]
        
        print(f"Found {len(confident_freqs)} confident detections")
        print()
        
        
        print("First 10 detections:")
        for i in range(min(10, len(confident_freqs))):
            note = frequency_to_note_name(confident_freqs[i])
            print(f"  Time: {confident_times[i]:.2f}s | "
                  f"Freq: {confident_freqs[i]:.2f} Hz | "
                  f"Note: {note} | "
                  f"Confidence: {confident_confs[i]:.2%}")
        
        
        avg_freq = np.mean(confident_freqs)
        avg_note = frequency_to_note_name(avg_freq)
        print()
        print(f"🎼 Average detected frequency: {avg_freq:.2f} Hz ({avg_note})")
        
    else:
        print("❌ No confident detections found")
    
    print()
    print("=" * 50)
    print("✅ Test completed successfully!")
    

def frequency_to_note_name(freq):
    """
    Convert frequency (Hz) to note name
    
    Args:
        freq: Frequency in Hz
        
    Returns:
        Note name (e.g., 'C4', 'G#3')
    """
    if freq <= 0:
        return "N/A"
    
    
    A4 = 440.0
    C0 = A4 * pow(2, -4.75)
    
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    h = round(12 * np.log2(freq / C0))
    octave = h // 12
    n = h % 12
    
    return note_names[n] + str(octave)


if __name__ == "__main__":

    audio_file = "tests/315706__spitefuloctopus__acousticguitar-c-chord.wav"
    
    
    test_audio_transcription(audio_file)