import { useState, useEffect } from 'react';
import { bridgeClient } from '../services/SimBridgeClient';

export interface BridgeStatus {
    connected: boolean;
    message: string;
    serverTime?: string;
    error?: string;
}

export function useSimBridge() {
    const [status, setStatus] = useState<BridgeStatus>({ connected: false, message: 'Connecting...' });

    useEffect(() => {
        const checkConnection = async () => {
            try {
                const response = await bridgeClient.ping();
                setStatus({
                    connected: true,
                    message: response.message,
                    serverTime: response.server_time
                });
            } catch (error) {
                setStatus({
                    connected: false,
                    message: 'Bridge Offline',
                    error: error instanceof Error ? error.message : 'Unknown error'
                });
            }
        };

        checkConnection();
        const interval = setInterval(checkConnection, 5000); // Poll every 5 seconds

        return () => clearInterval(interval);
    }, []);

    return { status, client: bridgeClient };
}
