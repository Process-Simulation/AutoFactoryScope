# AutoFactoryScope Web Frontend

TypeScript/React web frontend for the AutoFactoryScope robot detection system.

## Prerequisites

- Node.js 18+ and npm (or yarn/pnpm)

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Build

```bash
# Build for production
npm run build
```

## Configuration

Set the `VITE_API_URL` environment variable to point to your backend API (default: `http://localhost:8000`).

Create a `.env` file:
```
VITE_API_URL=http://localhost:8000
```

- React 18+
- TypeScript
- Vite
- Modern ES6+

## SimBridge Integration

This application integrates with **SimBridge** to communicate with legacy Tecnomatix Process Simulate environments.

### Architecture
Frontend -> API Gateway (:3001) -> SimBridge Server (:50051) -> Tecnomatix (.NET 4.8)

### Usage
The **SimBridge Control Panel** is automatically displayed on the main page. It allows you to:
- Monitor connection status
- Load simulation studies (.cojt)
- Read/Write signal values
- Control simulation playback (Start/Stop/Reset)

### Requirements
Ensure the SimBridge backend is running:
1. Start SimBridge Server (`dotnet run` in `SimBridge/Server`)
2. Start API Gateway (`npm start` in `SimBridge/ApiGateway`)

