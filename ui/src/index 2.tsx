import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { theme } from '@/styles/theme';
import { AppLayout } from '@/components/Layout/AppLayout';
import { Dashboard } from '@/pages/Dashboard';
import { Views } from '@/pages/Views';
import { Query } from '@/pages/Query';
import { Health } from '@/pages/Health';
import { Settings } from '@/pages/Settings';

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/views" element={<Views />} />
            <Route path="/query" element={<Query />} />
            <Route path="/health" element={<Health />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </AppLayout>
      </Router>
    </ThemeProvider>
  );
};

const container = document.getElementById('root');
if (!container) {
  throw new Error('Root element not found');
}

const root = createRoot(container);
root.render(<App />);