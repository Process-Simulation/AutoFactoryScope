const API_BASE_URL = 'http://localhost:3001/api';

export class SimBridgeClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    async ping(): Promise<{ message: string; server_time: string }> {
        const response = await fetch(`${this.baseUrl}/ping`);
        if (!response.ok) throw new Error('Failed to ping');
        return response.json();
    }

    async loadStudy(studyPath: string): Promise<{ success: boolean; message: string; loaded_entities_count: number }> {
        const response = await fetch(`${this.baseUrl}/load-study`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ studyPath })
        });
        if (!response.ok) throw new Error('Failed to load study');
        return response.json();
    }

    async getSignalValues(signalNames: string[]): Promise<{ values: Record<string, string> }> {
        const response = await fetch(`${this.baseUrl}/get-signals`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ signalNames })
        });
        if (!response.ok) throw new Error('Failed to get signals');
        return response.json();
    }

    async runSimulation(action: 'START' | 'STOP' | 'RESET' | 'STEP_FORWARD', speed: number = 1.0): Promise<{ success: boolean; state: string }> {
        const response = await fetch(`${this.baseUrl}/run-simulation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, speed })
        });
        if (!response.ok) throw new Error('Failed to run simulation');
        return response.json();
    }

    async captureLayout(): Promise<{ success: boolean; imageBlob: Blob; metadata: { studyName: string; timestamp: string } }> {
        // In a real implementation, this would call the SimBridge server
        // const response = await fetch(`${this.baseUrl}/capture-layout`);

        // MOCK IMPLEMENTATION for demonstration
        // Returns a dummy 1x1 pixel image blob
        return new Promise((resolve) => {
            setTimeout(() => {
                const canvas = document.createElement('canvas');
                canvas.width = 512;
                canvas.height = 512;
                const ctx = canvas.getContext('2d');
                if (ctx) {
                    ctx.fillStyle = '#e0e0e0';
                    ctx.fillRect(0, 0, 512, 512);
                    ctx.fillStyle = 'red';
                    ctx.fillRect(50, 50, 20, 20); // Dummy robot
                    ctx.fillStyle = 'blue';
                    ctx.font = '20px Arial';
                    ctx.fillText('SimBridge Capture', 20, 30);
                }

                canvas.toBlob((blob) => {
                    if (blob) {
                        resolve({
                            success: true,
                            imageBlob: blob,
                            metadata: {
                                studyName: 'Demo_Study_Automated_V1.cojt',
                                timestamp: new Date().toISOString()
                            }
                        });
                    } else {
                        throw new Error('Failed to generate mock blob');
                    }
                }, 'image/png');
            }, 800); // Simulate network delay
        });
    }
}

export const bridgeClient = new SimBridgeClient();

