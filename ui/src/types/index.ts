export interface ConversationEntry {
  entry_id: string;
  session_id: string;
  interaction_id: number;
  question: string;
  answer: string;
  question_timestamp: string;
  answer_timestamp: string;
  duration_seconds: number;
  action_type: string;
  location_id?: string;
  region_id?: string;
  group_id?: string;
  district_id?: string;
  sources?: Source[];
  date: string;
  hour: number;
}

export interface Source {
  name: string;
  relevance_score: number;
}

export interface ViewInfo {
  view_name: string;
  description: string;
  columns: string[];
  created_at: string;
}

export interface QueryResponse<T = any> {
  data: T[];
  row_count: number;
  execution_time_ms: number;
  query?: string;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  services: {
    duckdb: {
      status: string;
      version?: string;
    };
    s3: {
      status: string;
      bucket_accessible?: boolean;
    };
  };
}

export interface DashboardMetrics {
  totalConversations: number;
  totalSessions: number;
  avgInteractionsPerSession: number;
  topActions: Array<{
    action_type: string;
    count: number;
    percentage: number;
  }>;
  dailyStats: Array<{
    date: string;
    conversation_count: number;
    session_count: number;
  }>;
  locationStats: Array<{
    location_id: string;
    conversation_count: number;
  }>;
}

export interface ApiError {
  error: string;
  detail?: string;
  status_code?: number;
}