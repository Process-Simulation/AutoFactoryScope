import { useEffect, useMemo, useRef, useState } from 'react'
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

interface PreviewResponse {
  image_base64: string
  image_width: number
  image_height: number
}

interface CropRect {
  x: number
  y: number
  width: number
  height: number
}

type DragMode = 'draw' | 'move' | 'resize'
type ResizeHandle = 'nw' | 'ne' | 'sw' | 'se'

interface DragState {
  mode: DragMode
  handle?: ResizeHandle
  startX: number
  startY: number
  startCrop: CropRect | null
}

const clamp = (value: number, min: number, max: number) =>
  Math.min(Math.max(value, min), max)

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [crop, setCrop] = useState<CropRect | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DetectionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [displaySize, setDisplaySize] = useState({ width: 0, height: 0 })

  const imageRef = useRef<HTMLImageElement | null>(null)
  const dragStateRef = useRef<DragState | null>(null)
  const activePointerRef = useRef<number | null>(null)

  useEffect(() => {
    if (!preview || !imageRef.current) {
      setDisplaySize({ width: 0, height: 0 })
      return
    }

    const updateSize = () => {
      if (!imageRef.current) return
      const rect = imageRef.current.getBoundingClientRect()
      setDisplaySize({ width: rect.width, height: rect.height })
    }

    updateSize()
    const observer = new ResizeObserver(updateSize)
    observer.observe(imageRef.current)
    window.addEventListener('resize', updateSize)

    return () => {
      observer.disconnect()
      window.removeEventListener('resize', updateSize)
    }
  }, [preview])

  const loadPreview = async (selectedFile: File) => {
    setPreviewLoading(true)
    setPreviewError(null)
    setPreview(null)
    setCrop(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(`${API_URL}/preview`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Preview failed (HTTP ${response.status})`)
      }

      const data: PreviewResponse = await response.json()
      setPreview(data)
    } catch (err) {
      setPreviewError(err instanceof Error ? err.message : 'Failed to load preview')
    } finally {
      setPreviewLoading(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      setFile(selectedFile)
      setResult(null)
      setError(null)
      setPreviewError(null)
      setPreview(null)
      setCrop(null)
      void loadPreview(selectedFile)
    }
  }

  const minSelectionPx = 24

  const getPointerPosition = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!imageRef.current) {
      return { x: 0, y: 0, width: 0, height: 0 }
    }
    const rect = imageRef.current.getBoundingClientRect()
    return {
      x: clamp(event.clientX - rect.left, 0, rect.width),
      y: clamp(event.clientY - rect.top, 0, rect.height),
      width: rect.width,
      height: rect.height,
    }
  }

  const isPointInsideCrop = (
    x: number,
    y: number,
    width: number,
    height: number,
    rect: CropRect,
  ) => {
    const left = rect.x * width
    const top = rect.y * height
    const right = left + rect.width * width
    const bottom = top + rect.height * height
    return x >= left && x <= right && y >= top && y <= bottom
  }

  const handleCropPointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!preview || !imageRef.current) return
    if (event.button !== 0) return
    if (activePointerRef.current !== null) return

    const target = event.target as HTMLElement
    const handle = target.dataset.handle as ResizeHandle | undefined
    const { x, y, width, height } = getPointerPosition(event)
    if (!width || !height) return

    const startCrop = crop
    if (handle && startCrop) {
      dragStateRef.current = { mode: 'resize', handle, startX: x, startY: y, startCrop }
    } else if (startCrop && isPointInsideCrop(x, y, width, height, startCrop)) {
      dragStateRef.current = { mode: 'move', startX: x, startY: y, startCrop }
    } else {
      const startX = x / width
      const startY = y / height
      dragStateRef.current = { mode: 'draw', startX: x, startY: y, startCrop: null }
      setCrop({ x: startX, y: startY, width: 0, height: 0 })
    }

    activePointerRef.current = event.pointerId
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  const handleCropPointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    if (activePointerRef.current !== event.pointerId) return
    if (!dragStateRef.current || !imageRef.current) return

    const { x, y, width, height } = getPointerPosition(event)
    if (!width || !height) return

    const minNormW = minSelectionPx / width
    const minNormH = minSelectionPx / height
    const state = dragStateRef.current

    if (state.mode === 'draw') {
      const left = Math.min(state.startX, x)
      const right = Math.max(state.startX, x)
      const top = Math.min(state.startY, y)
      const bottom = Math.max(state.startY, y)

      const newX = clamp(left / width, 0, 1)
      const newY = clamp(top / height, 0, 1)
      const newWidth = clamp((right - left) / width, 0, 1 - newX)
      const newHeight = clamp((bottom - top) / height, 0, 1 - newY)

      setCrop({ x: newX, y: newY, width: newWidth, height: newHeight })
      return
    }

    if (!state.startCrop) return
    const startCrop = state.startCrop

    if (state.mode === 'move') {
      const dx = (x - state.startX) / width
      const dy = (y - state.startY) / height
      const newX = clamp(startCrop.x + dx, 0, 1 - startCrop.width)
      const newY = clamp(startCrop.y + dy, 0, 1 - startCrop.height)
      setCrop({ ...startCrop, x: newX, y: newY })
      return
    }

    if (state.mode === 'resize' && state.handle) {
      const pointerX = x / width
      const pointerY = y / height
      const startX = startCrop.x
      const startY = startCrop.y
      const startW = startCrop.width
      const startH = startCrop.height

      if (state.handle === 'nw') {
        const newX = clamp(pointerX, 0, startX + startW - minNormW)
        const newY = clamp(pointerY, 0, startY + startH - minNormH)
        setCrop({
          x: newX,
          y: newY,
          width: startX + startW - newX,
          height: startY + startH - newY,
        })
      } else if (state.handle === 'ne') {
        const newRight = clamp(pointerX, startX + minNormW, 1)
        const newY = clamp(pointerY, 0, startY + startH - minNormH)
        setCrop({
          x: startX,
          y: newY,
          width: newRight - startX,
          height: startY + startH - newY,
        })
      } else if (state.handle === 'sw') {
        const newX = clamp(pointerX, 0, startX + startW - minNormW)
        const newBottom = clamp(pointerY, startY + minNormH, 1)
        setCrop({
          x: newX,
          y: startY,
          width: startX + startW - newX,
          height: newBottom - startY,
        })
      } else if (state.handle === 'se') {
        const newRight = clamp(pointerX, startX + minNormW, 1)
        const newBottom = clamp(pointerY, startY + minNormH, 1)
        setCrop({
          x: startX,
          y: startY,
          width: newRight - startX,
          height: newBottom - startY,
        })
      }
    }
  }

  const handleCropPointerUp = (event: React.PointerEvent<HTMLDivElement>) => {
    if (activePointerRef.current !== event.pointerId) return
    const { width, height } = getPointerPosition(event)
    if (crop && width && height) {
      const minNormW = minSelectionPx / width
      const minNormH = minSelectionPx / height
      if (crop.width < minNormW || crop.height < minNormH) {
        setCrop(null)
      }
    }

    dragStateRef.current = null
    activePointerRef.current = null
    try {
      event.currentTarget.releasePointerCapture(event.pointerId)
    } catch {
      // no-op
    }
  }

  const cropMetrics = useMemo(() => {
    if (!preview || !crop) return null
    return {
      x: Math.round(crop.x * preview.image_width),
      y: Math.round(crop.y * preview.image_height),
      width: Math.round(crop.width * preview.image_width),
      height: Math.round(crop.height * preview.image_height),
    }
  }, [preview, crop])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    if (!crop) {
      setError('Please draw a crop area before running detection.')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append(
        'crop',
        JSON.stringify({
          x: Number(crop.x.toFixed(6)),
          y: Number(crop.y.toFixed(6)),
          width: Number(crop.width.toFixed(6)),
          height: Number(crop.height.toFixed(6)),
        }),
      )

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

          {previewLoading && (
            <div className="preview-status">Rendering preview...</div>
          )}

          {previewError && (
            <div className="error-message">
              <strong>Error:</strong> {previewError}
            </div>
          )}

          {preview && (
            <section className="crop-section">
              <h2>Select Layout Area</h2>
              <p className="crop-help">
                Draw a rectangle around the factory layout. The model will
                analyze only this region.
              </p>

              <div className="crop-stage">
                <div
                  className="crop-image-wrapper"
                  onPointerDown={handleCropPointerDown}
                  onPointerMove={handleCropPointerMove}
                  onPointerUp={handleCropPointerUp}
                  onPointerLeave={handleCropPointerUp}
                  onPointerCancel={handleCropPointerUp}
                >
                  <img
                    ref={imageRef}
                    src={`data:image/png;base64,${preview.image_base64}`}
                    alt="Preview for crop selection"
                    className="preview-image"
                  />

                  {crop && (
                    <div
                      className="crop-selection"
                      style={{
                        left: `${crop.x * displaySize.width}px`,
                        top: `${crop.y * displaySize.height}px`,
                        width: `${crop.width * displaySize.width}px`,
                        height: `${crop.height * displaySize.height}px`,
                      }}
                    >
                      <span className="crop-handle handle-nw" data-handle="nw" />
                      <span className="crop-handle handle-ne" data-handle="ne" />
                      <span className="crop-handle handle-sw" data-handle="sw" />
                      <span className="crop-handle handle-se" data-handle="se" />
                    </div>
                  )}
                </div>
              </div>

              <div className="crop-actions">
                <div className="crop-metrics">
                  {cropMetrics ? (
                    <span>
                      X: {cropMetrics.x}px, Y: {cropMetrics.y}px, W:{' '}
                      {cropMetrics.width}px, H: {cropMetrics.height}px
                    </span>
                  ) : (
                    <span>Click and drag to select the layout area.</span>
                  )}
                </div>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setCrop(null)}
                  disabled={!crop}
                >
                  Reset Selection
                </button>
              </div>
            </section>
          )}

          <button
            type="submit"
            disabled={!file || loading || previewLoading || !crop}
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

