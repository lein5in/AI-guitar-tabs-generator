from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
import shutil
from pathlib import Path

from app.core.transcriber import AudioTranscriber
from app.core.tab_generator import TabGenerator
from app.core.tuning_detector import TuningDetector
from app.core.audio_separator import AudioSeparator

app = FastAPI(
    title="Fretify API",
    description="AI powered guitar transcription API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

transcriber = AudioTranscriber()
tab_generator = TabGenerator()
tuning_detector = TuningDetector()
audio_separator = AudioSeparator()

ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.mp4', '.mov', '.avi', '.mkv', '.webm'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


@app.get("/")
async def root():
    return {
        "message": "Welcome to Fretify API!",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Fretify is running!"
    }


@app.get("/api/v1/info")
async def info():
    return {
        "name": "Fretify API",
        "version": "0.1.0",
        "endpoints": [
            "/",
            "/health",
            "/api/v1/info",
            "/api/v1/transcribe",
            "/api/v1/detect-tuning",
            "/api/v1/tunings",
            "/api/v1/formats",
            "/docs"
        ]
    }


@app.post("/api/v1/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    max_gap: float = 1.0,
    min_duration: float = 0.1,
    chord_window: float = 0.6,
    max_fret: int = 12,
    use_separation: bool = True
):
    """
    Transcribe an audio or video file to guitar tablature.
    Automatically detects tuning and capo position.
    
    Parameters:
    - file: Audio/Video file (MP3, WAV, FLAC, MP4, MOV, etc.)
    - max_gap: Maximum time gap to keep processing (seconds)
    - min_duration: Minimum note duration to include (seconds)
    - chord_window: Time window to group notes as chord (seconds)
    - max_fret: Maximum fret number to consider (default 12)
    - use_separation: Separate guitar from other instruments using AI (default True)
    """
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    temp_file = None
    processed_audio = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp:
            temp_file = temp.name
            shutil.copyfileobj(file.file, temp)
        
        file_size = os.path.getsize(temp_file)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f} MB"
            )
        
        print(f"📁 Processing file: {file.filename} ({file_size / (1024*1024):.1f} MB)")
        
        is_video = file_ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        
        if is_video or use_separation:
            print(f"🎬 Step 0: Processing file...")
            processed_audio = audio_separator.process_file(
                temp_file, 
                separate_instruments=use_separation
            )
            print(f"   ✅ Processed audio: {processed_audio}")
        else:
            processed_audio = temp_file
        
        # Étape 1: Transcrire
        print("🎵 Step 1: Transcribing audio with basic-pitch...")
        transcription_result = transcriber.transcribe_audio(processed_audio)
        
        # Étape 2: Détecter le tuning ET le capo
        print("🎵 Step 2: Detecting tuning and capo...")
        tuning_result = tuning_detector.detect_tuning(transcription_result['notes'])
        detected_capo = tuning_result.get('capo', 0)
        
        if detected_capo > 0:
            print(f"   🎸 {tuning_result['capo_label']} detected!")
        
        # Étape 3: Générer les tabs (avec capo)
        print("🎸 Step 3: Generating tablature...")
        tab_data = tab_generator.generate_tab_from_midi_notes(
            transcription_result['notes'],
            min_duration=min_duration,
            chord_window=chord_window,
            max_fret=max_fret,
            max_gap=max_gap,
            capo=detected_capo  # ← transmis au générateur
        )
        
        # Étape 4: ASCII tab (avec indicateur capo si présent)
        ascii_tab = tab_generator.format_tab_ascii(tab_data, capo=detected_capo)
        
        # Grouper en accords pour l'analyse
        chords = tab_generator.group_into_chords(transcription_result['notes'], chord_window)
        
        print(f"✅ Transcription complete: {len(tab_data)} positions, {len(chords)} chord(s)")
        
        response = {
            "success": True,
            "filename": file.filename,
            "file_size": file_size,
            "file_type": "video" if is_video else "audio",
            "separation_used": use_separation,
            "duration": transcription_result['duration'],
            "sample_rate": transcription_result['sample_rate'],
            "tuning": {
                "detected": tuning_result['detected_tuning'],
                "confidence": tuning_result['confidence'],
                "notes": tuning_result['tuning_notes'],
                "capo": detected_capo,                      # ← nouveau
                "capo_label": tuning_result['capo_label']   # ← nouveau
            },
            "stats": {
                "total_notes_detected": len(transcription_result['notes']),
                "tab_positions": len(tab_data),
                "chords_detected": len(chords)
            },
            "tablature": {
                "ascii": ascii_tab,
                "data": tab_data
            },
            "chords": [
                {
                    "index": i,
                    "start_time": chord[0]['start_time'],
                    "notes": [n['note_name'] for n in chord],
                    "midi_notes": [n['midi_note'] for n in chord]
                }
                for i, chord in enumerate(chords[:10])
            ]
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        print(f"❌ Error during transcription: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )
    
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
                print(f"🗑️ Cleaned up temp file")
            except Exception as e:
                print(f"⚠️ Failed to delete temp file: {e}")
        
        if processed_audio and processed_audio != temp_file and os.path.exists(processed_audio):
            try:
                os.unlink(processed_audio)
                print(f"🗑️ Cleaned up processed audio")
            except Exception as e:
                print(f"⚠️ Failed to delete processed audio: {e}")


@app.post("/api/v1/detect-tuning")
async def detect_tuning_only(
    file: UploadFile = File(...),
):
    """
    Detect guitar tuning and capo from an audio file without full transcription.
    """
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp:
            temp_file = temp.name
            shutil.copyfileobj(file.file, temp)
        
        file_size = os.path.getsize(temp_file)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f} MB"
            )
        
        print(f"🎸 Detecting tuning for: {file.filename}")
        
        transcription_result = transcriber.transcribe_audio(temp_file)
        tuning_result = tuning_detector.detect_tuning(transcription_result['notes'])
        
        print(f"✅ Tuning detected: {tuning_result['detected_tuning']} ({tuning_result['confidence']:.1%}), capo: {tuning_result['capo_label']}")
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "tuning": tuning_result
        })
    
    except Exception as e:
        print(f"❌ Error during tuning detection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Tuning detection failed: {str(e)}"
        )
    
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                print(f"⚠️ Failed to delete temp file: {e}")


@app.get("/api/v1/tunings")
async def list_tunings():
    """Get list of all supported guitar tunings"""
    return {
        "tunings": tuning_detector.list_all_tunings(),
        "count": len(tuning_detector.COMMON_TUNINGS)
    }


@app.get("/api/v1/formats")
async def supported_formats():
    """Get list of supported audio and video formats"""
    audio_formats = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']
    video_formats = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    
    return {
        "audio_formats": audio_formats,
        "video_formats": video_formats,
        "all_supported": audio_formats + video_formats,
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        "features": {
            "audio_extraction": "Automatic audio extraction from video files",
            "instrument_separation": "AI-powered guitar isolation using Demucs",
            "tuning_detection": "Automatic guitar tuning detection",
            "capo_detection": "Automatic capo detection (positions 1-7)"  # ← nouveau
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)