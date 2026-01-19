import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from './App'

// Mock fetch
const fetchMock = vi.fn()
global.fetch = fetchMock

// Mock SimBridgePanel to verify integration
vi.mock('./components/SimBridgePanel', () => ({
    SimBridgePanel: ({ onLayoutCaptured }: { onLayoutCaptured?: (file: File) => void }) => (
        <div data-testid="sim-bridge-panel">
            <button
                data-testid="mock-capture-btn"
                onClick={() => {
                    const file = new File(['mock content'], 'captured.png', { type: 'image/png' });
                    if (onLayoutCaptured) onLayoutCaptured(file);
                }}
            >
                Simulate Capture
            </button>
        </div>
    )
}))

describe('App Integration', () => {
    beforeEach(() => {
        fetchMock.mockClear()

        // Mock FileReader
        class MockFileReader {
            onloadend: (() => void) | null = null;
            result: string = 'data:image/png;base64,mock';
            readAsDataURL() {
                setTimeout(() => {
                    if (this.onloadend) this.onloadend();
                }, 0);
            }
        }
        global.FileReader = MockFileReader as any;
    })

    it('renders the application header', () => {
        render(<App />)
        expect(screen.getByText(/AutoFactoryScope/i)).toBeInTheDocument()
        expect(screen.getByText(/Robot Detection System/i)).toBeInTheDocument()
    })

    it('handles manual file upload', async () => {
        render(<App />)
        const fileInput = screen.getByLabelText(/choose layout image/i)
        const file = new File(['dummy content'], 'test.png', { type: 'image/png' })

        // Button should NOT be visible initially
        expect(screen.queryByRole('button', { name: /detect robots/i })).not.toBeInTheDocument()

        fireEvent.change(fileInput, { target: { files: [file] } })

        // Button should appear after file selection
        expect(await screen.findByRole('button', { name: /detect robots/i })).toBeInTheDocument()
        expect(screen.getByAltText(/Preview/i)).toBeInTheDocument()
    })

    // MVP: SimBridge is concealed, so we skip this test for now
    it.skip('handles automated capture from SimBridge', async () => {
        render(<App />)

        // Mock successful API response for the auto-submit
        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                request_id: 'req-auto',
                robot_count: 3,
                detections: [],
                annotated_image: 'base64img',
                processing_time_ms: 50,
                image_size: [800, 600],
                model_version: '0.1.0'
            })
        })

        // Trigger capture via mock panel
        const captureBtn = screen.getByTestId('mock-capture-btn')
        fireEvent.click(captureBtn)





        // Use a more specific text match or check for loading spinner/text
        // "Processing Layout..." is inside the format
        await waitFor(() => {
            expect(screen.getByText(/Processing Layout/i)).toBeInTheDocument()
        })

        // Wait for results
        await waitFor(() => {
            expect(screen.getByText(/Analysis Results/i)).toBeInTheDocument()
            expect(screen.getByText('3')).toBeInTheDocument()
        }, { timeout: 3000 })
    })
})
