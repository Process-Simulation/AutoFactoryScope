import { useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface DetectionItem {
  x1: number
  y1: number
  x2: number
  y2: number
  score: number
  class_id: number
  label?: string
}

interface DetectionResponse {
  robot_count: number
  detections: DetectionItem[]
  annotated_image_base64: string
  image_width: number
  image_height: number
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DetectionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setResult(null)
      setError(null)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_URL}/detect`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: DetectionResponse = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!result?.annotated_image_base64) return

    try {
      // Convert base64 to blob
      const byteCharacters = atob(result.annotated_image_base64)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: 'image/png' })

      // Create download link
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `robot_detection_${Date.now()}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download image')
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏭 AutoFactoryScope</h1>
        <p>Intelligent Factory Layout Robot Detection System</p>
      </header>

      <main className="app-main">
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-container">
            <label htmlFor="file-upload" className="file-label">
              {file ? file.name : 'Choose layout image...'}
            </label>
            <input
              id="file-upload"
              type="file"
              accept="image/*,application/pdf"
              onChange={handleFileChange}
              className="file-input"
            />
          </div>

          <button
            type="submit"
            disabled={!file || loading}
            className="submit-button"
          >
            {loading ? 'Processing...' : 'Detect Robots'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="results">
            <h2>Detection Results</h2>
            <div className="statistics">
              <p><strong>Robots Detected:</strong> {result.robot_count}</p>
              <p><strong>Total Detections:</strong> {result.detections.length}</p>
              <p><strong>Image Dimensions:</strong> {result.image_width} × {result.image_height} px</p>
            </div>

            <button
              onClick={handleDownload}
              className="download-button"
            >
              📥 Download Annotated Image
            </button>

            {result.annotated_image_base64 && (
              <div className="annotated-image">
                <h3>Annotated Layout</h3>
                <img
                  src={`data:image/png;base64,${result.annotated_image_base64}`}
                  alt="Annotated layout with robot detections"
                  className="result-image"
                />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App

