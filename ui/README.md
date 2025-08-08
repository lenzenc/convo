# Conversation Analytics UI

A modern React-based operational dashboard for conversation analytics data, built with TypeScript, Material-UI, and integrated with a FastAPI backend.

## Features

- **Operational Dashboard**: Real-time metrics and KPIs for conversation analytics
- **Data Visualization**: Interactive charts and graphs using Recharts
- **Database Views**: Browse and execute pre-built database views
- **AI-Powered Querying**: Natural language queries converted to SQL
- **System Health Monitoring**: Real-time health status of backend services
- **Modern UI**: Material-UI components with responsive design
- **Type Safety**: Full TypeScript implementation

## Technology Stack

- **React 18+** - Modern React with hooks and functional components
- **TypeScript** - Type safety and modern JavaScript features
- **Webpack 5** - Module bundler with hot module replacement
- **Material-UI v6+** - Comprehensive UI component library
- **Zustand** - Lightweight state management
- **React Router** - Client-side routing
- **Recharts** - Data visualization library
- **Axios** - HTTP client for API integration

## Prerequisites

- **Node.js 18+** - Required runtime version
- **npm 8+** - Package manager
- **FastAPI Backend** - Must be running on http://localhost:8000

## Installation

1. **Navigate to the UI directory:**
   ```bash
   cd ui
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   Navigate to http://localhost:3000

## Available Scripts

```bash
# Development
npm start              # Start development server with hot reloading
npm run build:dev      # Build for development

# Production
npm run build          # Build for production

# Code Quality
npm run lint           # Run ESLint and fix issues
npm run lint:check     # Check for lint issues without fixing
npm run format         # Format code with Prettier
npm run format:check   # Check code formatting
npm run type-check     # Run TypeScript type checking

# Utilities
npm run clean          # Clean build directory
```

## Project Structure

```
ui/
├── src/
│   ├── components/        # Reusable React components
│   │   ├── Layout/        # Layout components (AppLayout)
│   │   └── Dashboard/     # Dashboard-specific components
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx  # Main dashboard page
│   │   ├── Views.tsx      # Database views page
│   │   ├── Query.tsx      # AI query interface
│   │   ├── Health.tsx     # System health monitoring
│   │   └── Settings.tsx   # Application settings
│   ├── stores/           # Zustand stores
│   │   └── appStore.ts    # Main application state
│   ├── utils/            # Utility functions
│   │   ├── api.ts         # API service layer
│   │   └── formatters.ts  # Data formatting utilities  
│   ├── types/            # TypeScript type definitions
│   │   └── index.ts       # Shared interfaces and types
│   ├── styles/           # Styling and theming
│   │   └── theme.ts       # Material-UI theme configuration
│   ├── hooks/            # Custom React hooks
│   ├── assets/           # Static assets
│   └── index.tsx         # Application entry point
├── public/               # Static files
├── build/                # Production build output
├── webpack.config.js     # Webpack configuration
├── tsconfig.json         # TypeScript configuration
├── .eslintrc.json        # ESLint configuration
├── .prettierrc           # Prettier configuration
└── package.json          # Dependencies and scripts
```

## API Integration

The UI integrates with the FastAPI backend through a configured API service:

- **Base URL**: http://localhost:8000 (development)
- **Endpoints**:
  - `GET /health` - System health status
  - `GET /views` - List available database views
  - `GET /views/{name}/execute` - Execute a specific view
  - `GET /query` - Natural language query interface

### Proxy Configuration

The Webpack dev server includes proxy configuration to route `/api/*` requests to the FastAPI backend, avoiding CORS issues during development.

## State Management

The application uses Zustand for state management with the following stores:

- **AppStore**: Main application state including health status, views, dashboard metrics, and UI state

## Styling and Theming

- **Material-UI Theme**: Custom theme with operational dashboard styling
- **Responsive Design**: Mobile-first responsive layout
- **Dark/Light Mode**: Ready for theme switching (can be extended)

## Development Workflow

1. **Start the FastAPI backend** (see main project README)
2. **Start the UI development server**: `npm start`
3. **Make changes** - Hot reloading will refresh the browser
4. **Run code quality checks**: `npm run lint && npm run type-check`
5. **Build for production**: `npm run build`

## Environment Variables

- **NODE_ENV**: Set automatically by build scripts
- **Development API**: http://localhost:8000
- **Production API**: `/api` (proxied)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Common Issues

1. **Port 3000 already in use:**
   ```bash
   # The dev server will automatically try port 3001, 3002, etc.
   # Or specify a different port:
   PORT=3001 npm start
   ```

2. **API connection errors:**
   - Ensure FastAPI backend is running on port 8000
   - Check proxy configuration in webpack.config.js
   - Verify CORS settings in the FastAPI backend

3. **Build errors:**
   ```bash
   # Clean and reinstall dependencies
   npm run clean
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **TypeScript errors:**
   ```bash
   # Run type checking
   npm run type-check
   ```

## Contributing

1. Follow the existing code style and patterns
2. Run linting and type checking before committing
3. Ensure all pages work with the backend API
4. Test responsive design across different screen sizes

## Performance Optimization

- Code splitting with Webpack
- Lazy loading of routes (can be extended)
- Optimized bundle sizes with separate vendor chunks
- Production builds include minification and compression

## Future Enhancements

- Real-time updates with WebSocket integration
- Advanced filtering and search capabilities
- Export functionality for charts and data
- User authentication and role-based access
- Customizable dashboard layouts
- Mobile app version with React Native