"""
Audio separation module using Demucs
Separates audio into stems: vocals, drums, bass, and other (guitar)
"""

import os
import torch
import subprocess
from pathlib import Path
import tempfile
import shutil


class AudioSeparator:
    """
    Separates audio tracks using Demucs (Meta's AI model)
    """
    
    def __init__(self, model_name='htdemucs'):
        """
        Initialize the audio separator
        
        Args:
            model_name: Demucs model to use ('htdemucs' is default and best)
        """
        self.model_name = model_name
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🎵 AudioSeparator initialized (device: {self.device})")
    
    def separate_audio(self, audio_path, output_dir=None, extract_guitar=True):
        """
        Separate audio into stems using Demucs
        
        Args:
            audio_path: Path to input audio file
            output_dir: Directory to save separated stems (temp if None)
            extract_guitar: If True, return only the guitar/other track
            
        Returns:
            dict: {
                'vocals': path,
                'drums': path,
                'bass': path,
                'other': path,  # Usually contains guitar
                'guitar': path  # Alias for 'other'
            }
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Create temp output directory if not provided
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix='demucs_')
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"🎸 Separating audio with Demucs ({self.model_name})...")
        print(f"   Input: {audio_path}")
        print(f"   Output: {output_dir}")
        
        try:
            # Construire la commande demucs
            cmd = [
                'demucs',
                '--two-stems', 'other',  # Sépare seulement vocals vs other (plus rapide)
                '-n', self.model_name,
                '--out', output_dir,
                '--mp3',  # Forcer sortie MP3 au lieu de WAV (évite problème torchcodec)
                '--mp3-bitrate', '320',
                audio_path
            ]
            
            # Si on a un GPU, utiliser CUDA
            if self.device == 'cuda':
                cmd.insert(1, '--device')
                cmd.insert(2, 'cuda')
            
            print(f"   Running: {' '.join(cmd)}")
            
            # Exécuter demucs
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✅ Separation complete!")
            
            # Trouver les fichiers de sortie
            # Demucs crée : output_dir/htdemucs/filename/vocals.wav et other.wav
            audio_name = Path(audio_path).stem
            stem_dir = Path(output_dir) / self.model_name / audio_name
            
            if not stem_dir.exists():
                raise FileNotFoundError(f"Demucs output directory not found: {stem_dir}")
            
            # Chemins des stems (MP3 au lieu de WAV)
            stems = {
                'vocals': str(stem_dir / 'vocals.mp3'),
                'other': str(stem_dir / 'other.mp3'),
                'guitar': str(stem_dir / 'other.mp3')  # Alias
            }
            
            # Vérifier que les fichiers existent
            for stem_name, stem_path in stems.items():
                if stem_name != 'guitar' and not os.path.exists(stem_path):
                    print(f"⚠️ Warning: {stem_name} stem not found at {stem_path}")
            
            print(f"   Stems saved:")
            for name, path in stems.items():
                if name != 'guitar' and os.path.exists(path):
                    size = os.path.getsize(path) / (1024 * 1024)  # MB
                    print(f"     {name:10s}: {size:.1f} MB")
            
            if extract_guitar:
                # Retourner seulement la piste guitare
                return stems['guitar']
            else:
                # Retourner tous les stems
                return stems
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Demucs failed:")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            raise RuntimeError(f"Demucs separation failed: {e.stderr}")
        
        except Exception as e:
            print(f"❌ Error during separation: {str(e)}")
            raise
    
    def extract_audio_from_video(self, video_path, output_path=None):
        """
        Extract audio from video file using ffmpeg
        
        Args:
            video_path: Path to video file (MP4, MOV, AVI, etc.)
            output_path: Output audio path (temp WAV if None)
            
        Returns:
            str: Path to extracted audio file
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Vérifier que ffmpeg est installé
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg:\n"
                "  Windows: winget install ffmpeg\n"
                "  Mac: brew install ffmpeg\n"
                "  Linux: sudo apt install ffmpeg"
            )
        
        # Créer un fichier de sortie temporaire si non fourni
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix='.wav', prefix='extracted_audio_')
            os.close(fd)
        
        print(f"🎥 Extracting audio from video...")
        print(f"   Input: {video_path}")
        print(f"   Output: {output_path}")
        
        try:
            # Commande ffmpeg pour extraire l'audio
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # Pas de vidéo
                '-acodec', 'pcm_s16le',  # WAV format
                '-ar', '44100',  # Sample rate
                '-ac', '2',  # Stereo
                '-y',  # Overwrite
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            print(f"✅ Audio extracted: {size:.1f} MB")
            
            return output_path
        
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg failed:")
            print(f"   stderr: {e.stderr}")
            raise RuntimeError(f"Audio extraction failed: {e.stderr}")
    
    def process_file(self, file_path, separate_instruments=True):
        """
        Process audio or video file
        
        Args:
            file_path: Path to audio or video file
            separate_instruments: If True, use Demucs to isolate guitar
            
        Returns:
            str: Path to processed audio file (guitar-only if separated)
        """
        file_ext = Path(file_path).suffix.lower()
        
        # Si c'est une vidéo, extraire l'audio d'abord
        if file_ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
            print("📹 Video file detected")
            audio_path = self.extract_audio_from_video(file_path)
        else:
            audio_path = file_path
        
        # Si séparation demandée, utiliser Demucs
        if separate_instruments:
            guitar_path = self.separate_audio(audio_path, extract_guitar=True)
            return guitar_path
        else:
            return audio_path


def test_audio_separator():
    """
    Test the audio separator
    """
    import sys
    
    print("=" * 60)
    print("Testing Audio Separator")
    print("=" * 60)
    print()
    
    # Test avec un fichier audio
    audio_file = "../tests/315706__spitefuloctopus__acousticguitar-c-chord.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ Test file not found: {audio_file}")
        return
    
    separator = AudioSeparator()
    
    print("Test 1: Separating audio into stems")
    print("-" * 60)
    
    try:
        stems = separator.separate_audio(audio_file, extract_guitar=False)
        
        print("\n✅ Separation successful!")
        print("\nGenerated stems:")
        for name, path in stems.items():
            if name != 'guitar' and os.path.exists(path):
                print(f"  {name}: {path}")
        
        print("\n" + "=" * 60)
        print("✅ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_audio_separator()