import { useSimBridge } from '../hooks/useSimBridge';
import './BridgeStatus.css';

export function BridgeStatus() {
    const { status, client } = useSimBridge();

    const testLoadStudy = async () => {
        try {
            const result = await client.loadStudy('C:\\Simulations\\Demo.cojt');
            alert(`Study Load: ${result.message}\nEntities: ${result.loaded_entities_count}`);
        } catch (error) {
            alert(`Error: ${error}`);
        }
    };

    const testSignals = async () => {
        try {
            const result = await client.getSignalValues(['Robot1_Ready', 'Line_Start']);
            alert(`Signals:\n${JSON.stringify(result.values, null, 2)}`);
        } catch (error) {
            alert(`Error: ${error}`);
        }
    };

    return (
        <div className="bridge-status">
            <div className={`status-indicator ${status.connected ? 'connected' : 'disconnected'}`}>
                <span className="status-dot"></span>
                <span className="status-text">{status.message}</span>
            </div>
            {status.serverTime && <div className="server-time">Server: {status.serverTime}</div>}
            {status.error && <div className="error-message">{status.error}</div>}
            {status.connected && (
                <div className="action-buttons">
                    <button onClick={testLoadStudy}>Test Load Study</button>
                    <button onClick={testSignals}>Test Get Signals</button>
                </div>
            )}
        </div>
    );
}
