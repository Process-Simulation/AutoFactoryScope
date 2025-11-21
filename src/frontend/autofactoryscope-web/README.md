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

## Technology Stack

- React 18+
- TypeScript
- Vite
- Modern ES6+

