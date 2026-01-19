import { useState } from 'react'
import { CloudUpload, Scan, Trash2, Microscope, ArrowRight, Loader2, AlertCircle } from 'lucide-react'
// import { SimBridgePanel } from './components/SimBridgePanel'

interface DetectionItem {
  bbox: [number, number, number, number];
  confidence: number;
  class_name: string;
}

interface DetectionResponse {
  request_id: string;
  robot_count: number;
  detections: DetectionItem[];
  annotated_image: string | null;
  processing_time_ms: number;
  image_size: [number, number];
  model_version: string;
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DetectionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Use environment variable for API URL or default to localhost
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      setFile(selectedFile)

      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(selectedFile)

      // Clear previous results/errors
      setResult(null)
      setError(null)
    }
  }

  /*
  const handleCapture = (capturedFile: File) => {
    setFile(capturedFile);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(capturedFile);

    // Clear previous results
    setResult(null);
    setError(null);

    // Auto-submit after capture
    // Pass file directly to avoid state race conditions
    handleSubmit(capturedFile);
  };
  */

  const handleRemoveFile = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
  }

  const handleSubmit = async (fileToSubmit?: File) => {
    const targetFile = fileToSubmit || file;
    if (!targetFile) return;

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', targetFile)
    // Request annotated image
    formData.append('include_annotated', 'true')

    try {

      const response = await fetch(`${API_URL}/detect`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData?.detail?.error?.message || `Error: ${response.statusText}`)
      }

      const data: DetectionResponse = await response.json()
      setResult(data)
    } catch (err) {
      console.error('Detection failed:', err)
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 front">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scan className="w-8 h-8 text-primary" />
            <div className="flex flex-col">
              <h1 className="text-xl font-bold leading-none tracking-tight">AutoFactoryScope</h1>
              <span className="text-xs text-muted-foreground font-medium tracking-wide text-gray-500">ROBOT DETECTION SYSTEM</span>
            </div>
          </div>
          <div className="text-sm text-gray-500 font-mono">v0.2.0-beta</div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-8 max-w-7xl">

        <section className="max-w-4xl mx-auto space-y-6">
          <div className="space-y-6">
            {/* File Upload / Preview Area */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden transition-all hover:shadow-xl">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <Microscope className="w-5 h-5 text-primary" />
                    Layout Analysis
                  </h2>
                  {result && (
                    <span className="bg-green-100 text-green-700 text-xs font-bold px-3 py-1 rounded-full border border-green-200 shadow-sm">
                      PROCESSING COMPLETE
                    </span>
                  )}
                </div>

                {!file ? (
                  <div className="border-2 border-dashed border-gray-300 hover:border-primary hover:bg-blue-50/50 rounded-xl p-12 transition-all duration-300 text-center group cursor-pointer relative">
                    <input
                      type="file"
                      id="layout-upload"
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                      onChange={handleFileChange}
                      accept="image/*"
                      aria-label="Choose layout image"
                    />
                    <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-inner">
                      <CloudUpload className="w-8 h-8 text-primary" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Upload Layout Image</h3>
                    <p className="text-gray-500 text-sm max-w-sm mx-auto">
                      Drag and drop your high-resolution factory layout (PNG, JPG) or click to browse.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-6 animate-in fade-in zoom-in duration-300">
                    {/* Image Preview / Result View */}
                    <div className="relative rounded-lg overflow-hidden bg-gray-900 aspect-video ring-1 ring-black/10 shadow-inner group">
                      {result?.annotated_image ? (
                        <img
                          src={`data:image/jpeg;base64,${result.annotated_image}`}
                          alt="Analyzed Layout"
                          className="w-full h-full object-contain"
                        />
                      ) : (
                        <img
                          src={preview || ''}
                          alt="Preview"
                          className={`w-full h-full object-contain transition-opacity duration-300 ${loading ? 'opacity-50 blur-sm' : ''}`}
                        />
                      )}

                      {/* Overlay Controls */}
                      <div className="absolute top-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={handleRemoveFile}
                          className="bg-white/90 hover:bg-white text-gray-700 p-2 rounded-full shadow-lg backdrop-blur-sm transition-all hover:text-red-600"
                          disabled={loading}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      {loading && (
                        <div className="absolute inset-0 flex items-center justify-center flex-col text-white">
                          <Loader2 className="w-12 h-12 animate-spin mb-4 text-primary" />
                          <div className="font-semibold text-lg tracking-wide">Processing Layout...</div>
                          <div className="text-sm opacity-80 mt-2">Running YOLOv8 Inference</div>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    {!result && (
                      <div className="flex justify-end pt-2">
                        <button
                          onClick={() => handleSubmit()}
                          disabled={loading}
                          className="bg-primary hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium shadow-lg shadow-blue-500/30 flex items-center gap-2 transition-all hover:translate-y-[-1px] active:translate-y-[1px] disabled:opacity-50 disabled:shadow-none"
                        >
                          {loading ? 'Analyzing...' : 'Detect Robots'}
                          {!loading && <ArrowRight className="w-4 h-4" />}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {error && (
                  <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3 text-red-700 animate-in slide-in-from-bottom-2">
                    <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                    <div className="text-sm font-medium">{error}</div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar / Info Panel - SimBridge Hidden for MVP */}
          <div className="space-y-6">

            {/* 
                <SimBridgePanel onLayoutCaptured={handleCapture} /> 
                */}


            {/* Detection Stats Card */}
            {result && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 animate-in slide-in-from-right duration-500">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Analysis Results</h3>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <div className="text-3xl font-bold text-primary mb-1">{result.robot_count}</div>
                    <div className="text-xs text-blue-600 font-medium">Robots Found</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="text-3xl font-bold text-gray-700 mb-1">{result.processing_time_ms}</div>
                    <div className="text-xs text-gray-500 font-medium">Time (ms)</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between text-sm py-2 border-b border-gray-100">
                    <span className="text-gray-500">Resolution</span>
                    <span className="font-mono font-medium">{result.image_size[0]} x {result.image_size[1]}</span>
                  </div>
                  <div className="flex justify-between text-sm py-2 border-b border-gray-100">
                    <span className="text-gray-500">Request ID</span>
                    <span className="font-mono text-xs text-gray-400" title={result.request_id}>{result.request_id.substring(0, 8)}...</span>
                  </div>
                  <div className="flex justify-between text-sm py-2 border-b border-gray-100">
                    <span className="text-gray-500">Model Version</span>
                    <span className="font-mono font-medium">{result.model_version}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

      </main>
    </div>
  )
}

export default App
