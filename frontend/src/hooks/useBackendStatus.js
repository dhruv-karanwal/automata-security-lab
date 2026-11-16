import { useState, useEffect, useCallback } from 'react';
import { getHealth, API_BASE_URL } from '../services/api.js';

/**
 * Hook to monitor and display connection status to FastAPI backend
 */
export function useBackendStatus() {
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [lastChecked, setLastChecked] = useState(null);
  const [error, setError] = useState(null);

  const checkConnection = useCallback(async () => {
    setIsChecking(true);
    try {
      const res = await getHealth();
      setIsConnected(true);
      setError(null);
      setLastChecked(new Date());
      return res;
    } catch (err) {
      setIsConnected(false);
      setError(err.message);
      setLastChecked(new Date());
      return null;
    } finally {
      setIsChecking(false);
    }
  }, []);

  useEffect(() => {
    checkConnection();
    // Poll every 30 seconds for state updates
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [checkConnection]);

  return {
    isConnected,
    isChecking,
    lastChecked,
    error,
    backendUrl: API_BASE_URL,
    checkConnection
  };
}
