import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { ViewInfo, HealthStatus, DashboardMetrics } from '@/types';
import ApiService from '@/utils/api';

interface AppState {
  // Health and system status
  health: HealthStatus | null;
  healthLoading: boolean;
  healthError: string | null;
  
  // Views
  views: ViewInfo[];
  viewsLoading: boolean;
  viewsError: string | null;
  
  // Dashboard metrics
  dashboardMetrics: DashboardMetrics | null;
  dashboardLoading: boolean;
  dashboardError: string | null;
  
  // UI state
  sidebarOpen: boolean;
  selectedView: string | null;
  
  // Actions
  fetchHealth: () => Promise<void>;
  fetchViews: () => Promise<void>;
  fetchDashboardMetrics: () => Promise<void>;
  setSidebarOpen: (open: boolean) => void;
  setSelectedView: (viewName: string | null) => void;
  clearErrors: () => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    (set, get) => ({
      // Initial state
      health: null,
      healthLoading: false,
      healthError: null,
      
      views: [],
      viewsLoading: false,
      viewsError: null,
      
      dashboardMetrics: null,
      dashboardLoading: false,
      dashboardError: null,
      
      sidebarOpen: true,
      selectedView: null,
      
      // Actions
      fetchHealth: async () => {
        set({ healthLoading: true, healthError: null });
        try {
          const health = await ApiService.getHealth();
          set({ health, healthLoading: false });
        } catch (error) {
          set({ 
            healthError: error instanceof Error ? error.message : 'Failed to fetch health status',
            healthLoading: false 
          });
        }
      },
      
      fetchViews: async () => {
        set({ viewsLoading: true, viewsError: null });
        try {
          const views = await ApiService.getViews();
          set({ views, viewsLoading: false });
        } catch (error) {
          set({ 
            viewsError: error instanceof Error ? error.message : 'Failed to fetch views',
            viewsLoading: false 
          });
        }
      },
      
      fetchDashboardMetrics: async () => {
        set({ dashboardLoading: true, dashboardError: null });
        try {
          // Fetch multiple views to build dashboard metrics
          const [
            interactionsData,
            popularActionsData,
            activeSessionsData,
            recentConversationsData
          ] = await Promise.all([
            ApiService.executeView('interactions_per_day', { limit: 30 }),
            ApiService.executeView('popular_actions'),
            ApiService.executeView('active_sessions', { limit: 100 }),
            ApiService.executeView('recent_conversations', { limit: 1000 })
          ]);
          
          // Calculate aggregate metrics
          const totalConversations = recentConversationsData.data.length;
          const uniqueSessions = new Set(recentConversationsData.data.map((d: any) => d.session_id)).size;
          const avgInteractionsPerSession = totalConversations / uniqueSessions || 0;
          
          const dashboardMetrics: DashboardMetrics = {
            totalConversations,
            totalSessions: uniqueSessions,
            avgInteractionsPerSession: Number(avgInteractionsPerSession.toFixed(2)),
            topActions: popularActionsData.data.slice(0, 5),
            dailyStats: interactionsData.data.slice(0, 7),
            locationStats: [] // Will be populated when location view is available
          };
          
          set({ dashboardMetrics, dashboardLoading: false });
        } catch (error) {
          set({ 
            dashboardError: error instanceof Error ? error.message : 'Failed to fetch dashboard metrics',
            dashboardLoading: false 
          });
        }
      },
      
      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
      },
      
      setSelectedView: (viewName: string | null) => {
        set({ selectedView: viewName });
      },
      
      clearErrors: () => {
        set({ healthError: null, viewsError: null, dashboardError: null });
      },
    }),
    {
      name: 'app-store',
    }
  )
);