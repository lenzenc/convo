import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Alert,
  AlertTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Switch,
  FormControlLabel,
  Chip,
} from '@mui/material';
import {
  Send as SendIcon,
  Code as CodeIcon,
  QueryStats as QueryStatsIcon,
} from '@mui/icons-material';
import { QueryResponse } from '@/types';
import ApiService from '@/utils/api';
import { formatNumber, formatDateTime } from '@/utils/formatters';

export const Query: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugMode, setDebugMode] = useState(false);

  const exampleQuestions = [
    'How many conversations are there?',
    'Show me conversations by date',
    'What are the most common user actions?',
    'Which sessions had more than 3 interactions?',
    'What questions were asked about inventory?',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setQueryResult(null);

    try {
      const result = await ApiService.query(question, { debug: debugMode });
      setQueryResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute query');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuestion: string) => {
    setQuestion(exampleQuestion);
  };

  const renderTable = (data: any[]) => {
    if (!data || data.length === 0) {
      return <Typography>No data returned</Typography>;
    }

    const columns = Object.keys(data[0]);

    return (
      <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell key={column}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {column}
                  </Typography>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, index) => (
              <TableRow key={index} hover>
                {columns.map((column) => (
                  <TableCell key={column}>
                    {typeof row[column] === 'number'
                      ? formatNumber(row[column])
                      : String(row[column] || '')}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI-Powered Query
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Ask questions about your conversation data in natural language
        </Typography>
      </Box>

      {/* Query Form */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              label="Ask a question about your conversation data"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., How many conversations happened last week?"
              sx={{ mb: 2 }}
            />
            
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <FormControlLabel
                control={
                  <Switch
                    checked={debugMode}
                    onChange={(e) => setDebugMode(e.target.checked)}
                  />
                }
                label="Show SQL query"
              />
              
              <Button
                type="submit"
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                disabled={loading || !question.trim()}
              >
                {loading ? 'Processing...' : 'Execute Query'}
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Example Questions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Example Questions
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {exampleQuestions.map((example, index) => (
              <Chip
                key={index}
                label={example}
                onClick={() => handleExampleClick(example)}
                clickable
                variant="outlined"
                sx={{ mb: 1 }}
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <AlertTitle>Query Error</AlertTitle>
          {error}
        </Alert>
      )}

      {/* Results */}
      {queryResult && (
        <Card>
          <CardContent>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                mb: 2,
              }}
            >
              <Typography variant="h6">
                Query Results
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  {formatNumber(queryResult.row_count)} rows
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {queryResult.execution_time_ms}ms
                </Typography>
              </Box>
            </Box>

            {/* Show SQL query if debug mode is on */}
            {debugMode && queryResult.query && (
              <Card variant="outlined" sx={{ mb: 2, bgcolor: 'grey.50' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CodeIcon sx={{ mr: 1 }} />
                    <Typography variant="subtitle2">Generated SQL Query</Typography>
                  </Box>
                  <Typography
                    component="pre"
                    variant="body2"
                    sx={{
                      fontFamily: 'monospace',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                    }}
                  >
                    {queryResult.query}
                  </Typography>
                </CardContent>
              </Card>
            )}

            {/* Data Table */}
            {renderTable(queryResult.data)}
          </CardContent>
        </Card>
      )}
    </Container>
  );
};