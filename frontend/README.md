# AI Document Generator Frontend

This is the frontend application for the AI-Assisted Document Authoring and Generation Platform, built with Next.js 16 and React 19.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
├── components/             # Reusable React components
├── lib/                    # API clients and utilities
│   ├── api.ts             # Main API client class
│   ├── auth-api.ts        # Authentication API methods
│   ├── projects-api.ts    # Project management API methods
│   ├── content-api.ts     # Content and refinement API methods
│   ├── utils.ts           # Utility functions
│   └── index.ts           # Main exports
├── types/                  # TypeScript type definitions
│   └── index.ts           # All interface definitions
├── public/                 # Static assets
└── ...config files
```

## Technology Stack

- **Next.js 16.0.3** - React framework with App Router
- **React 19.2.0** - UI library
- **TypeScript 5** - Type safety
- **Tailwind CSS 4** - Styling framework
- **ESLint** - Code linting

## Environment Variables

Copy `.env.example` to `.env.local` and configure:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## API Client Usage

The API client is configured to work with the FastAPI backend:

```typescript
import { authApi, projectsApi, contentApi } from '@/lib';

// Authentication
const response = await authApi.login({ email, password });

// Projects
const projects = await projectsApi.getProjects();

// Content refinement
const refined = await contentApi.refineSection(sectionId, { prompt });
```

## Type Safety

All API responses and data models are fully typed using TypeScript interfaces defined in `/types/index.ts`.