import { useState } from 'react';
import { useSimBridge } from '../hooks/useSimBridge';
import './SimBridgePanel.css';

export function SimBridgePanel() {
    const { status, client } = useSimBridge();
    const [studyPath, setStudyPath] = useState('C:\\Studies\\Sample.cojt');
    const [signalNames, setSignalNames] = useState('conveyor_speed, robot_status, cycle_time');
    const [signals, setSignals] = useState<Record<string, string>>({});
    const [simState, setSimState] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [logs, setLogs] = useState<string[]>([]);

    const addLog = (msg: string) => {
        setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 50));
    };

    const handleLoadStudy = async () => {
        setLoading(true);
        try {
            const result = await client.loadStudy(studyPath);
            addLog(`Study Loaded: ${result.message} (${result.loaded_entities_count} entities)`);
        } catch (error) {
            addLog(`Error loading study: ${error}`);
        } finally {
            setLoading(false);
        }
    };

    const handleGetSignals = async () => {
        const names = signalNames.split(',').map(s => s.trim()).filter(s => s);
        if (names.length === 0) return;

        try {
            const result = await client.getSignalValues(names);
            setSignals(result.values);
            addLog(`Signals updated: ${JSON.stringify(result.values)}`);
        } catch (error) {
            addLog(`Error getting signals: ${error}`);
        }
    };

    const handleSimControl = async (action: 'START' | 'STOP' | 'RESET' | 'STEP_FORWARD') => {
        try {
            const result = await client.runSimulation(action);
            setSimState(result.state);
            addLog(`Simulation ${action}: ${result.state}`);
        } catch (error) {
            addLog(`Error controlling simulation: ${error}`);
        }
    };

    return (
        <div className="simbridge-panel">
            <div className="panel-header">
                <h2>🌉 SimBridge Control</h2>
                <div className={`connection-badge ${status.connected ? 'connected' : 'disconnected'}`}>
                    {status.connected ? 'Connected' : 'Disconnected'}
                    {status.connected && status.message.includes('Mock') && ' (Mock)'}
                </div>
            </div>

            {status.serverTime && <div className="server-info">Server Time: {status.serverTime}</div>}

            <div className="panel-grid">
                {/* Study Control */}
                <div className="control-card">
                    <h3>📂 Load Study</h3>
                    <div className="input-group">
                        <input
                            type="text"
                            value={studyPath}
                            onChange={(e) => setStudyPath(e.target.value)}
                            placeholder="Path to .cojt"
                        />
                        <button onClick={handleLoadStudy} disabled={!status.connected || loading}>
                            {loading ? 'Loading...' : 'Load'}
                        </button>
                    </div>
                </div>

                {/* Simulation Control */}
                <div className="control-card">
                    <h3>▶️ Simulation</h3>
                    <div className="button-group">
                        <button className="btn-start" onClick={() => handleSimControl('START')} disabled={!status.connected}>Start</button>
                        <button className="btn-stop" onClick={() => handleSimControl('STOP')} disabled={!status.connected}>Stop</button>
                        <button className="btn-reset" onClick={() => handleSimControl('RESET')} disabled={!status.connected}>Reset</button>
                        <button className="btn-step" onClick={() => handleSimControl('STEP_FORWARD')} disabled={!status.connected}>Step</button>
                    </div>
                    {simState && <div className="state-display">State: {simState}</div>}
                </div>

                {/* Signal Monitoring */}
                <div className="control-card full-width">
                    <h3>📊 Signals</h3>
                    <div className="input-group">
                        <input
                            type="text"
                            value={signalNames}
                            onChange={(e) => setSignalNames(e.target.value)}
                            placeholder="Signal names (comma separated)"
                        />
                        <button onClick={handleGetSignals} disabled={!status.connected}>Refresh</button>
                    </div>
                    {Object.keys(signals).length > 0 && (
                        <div className="signals-grid">
                            {Object.entries(signals).map(([name, value]) => (
                                <div key={name} className="signal-item">
                                    <span className="signal-name">{name}</span>
                                    <span className="signal-value">{value}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Logs */}
                <div className="control-card full-width logs-card">
                    <h3>📝 Activity Log</h3>
                    <div className="logs-container">
                        {logs.length === 0 ? <div className="no-logs">No activity yet</div> : (
                            logs.map((log, i) => <div key={i} className="log-entry">{log}</div>)
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
