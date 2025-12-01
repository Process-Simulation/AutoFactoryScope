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
}

export const bridgeClient = new SimBridgeClient();

