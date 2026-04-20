import axios from 'axios'
import type { TranscribeResponse } from '../types'

const API_BASE = 'http://localhost:8000'

export async function transcribeAudio(
  file: File,
  options?: {
    max_gap?: number
    min_duration?: number
    chord_window?: number
    max_fret?: number
    use_separation?: boolean
  }
): Promise<TranscribeResponse> {
  const formData = new FormData()
  formData.append('file', file)

  if (options) {
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined) formData.append(key, String(value))
    })
  }

  const response = await axios.post<TranscribeResponse>(
    `${API_BASE}/api/v1/transcribe`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  )

  return response.data
}