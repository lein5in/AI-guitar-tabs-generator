export interface TuningResult {
  detected: string
  confidence: number
  notes: string[]
  capo: number
  capo_label: string
}

export interface TabNote {
  start_time: number
  end_time: number
  duration: number
  midi_note: number
  frequency: number
  note_name: string
  string: number
  fret: number
  fret_absolute: number
  velocity: number
}

export interface ChordGroup {
  index: number
  start_time: number
  notes: string[]
  midi_notes: number[]
}

export interface TranscribeStats {
  total_notes_detected: number
  tab_positions: number
  chords_detected: number
}

export interface TranscribeResponse {
  success: boolean
  filename: string
  file_size: number
  file_type: string
  separation_used: boolean
  duration: number
  sample_rate: number
  tuning: TuningResult
  stats: TranscribeStats
  tablature: {
    ascii: string
    data: TabNote[]
  }
  chords: ChordGroup[]
}

export type AppState = 'idle' | 'loading' | 'results' | 'error'