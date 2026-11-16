import React, { createContext, useContext, useReducer } from 'react';
import {
  createInitialEmailWorkspaceState,
  emailWorkspaceReducer,
} from './emailWorkspaceState.js';

const EmailWorkspaceContext = createContext(null);

export function EmailWorkspaceProvider({ children }) {
  const [state, dispatch] = useReducer(
    emailWorkspaceReducer,
    undefined,
    createInitialEmailWorkspaceState,
  );

  return (
    <EmailWorkspaceContext.Provider value={{ state, dispatch }}>
      {children}
    </EmailWorkspaceContext.Provider>
  );
}

export function useEmailWorkspace() {
  const workspace = useContext(EmailWorkspaceContext);
  if (!workspace) {
    throw new Error('useEmailWorkspace must be used inside EmailWorkspaceProvider');
  }
  return workspace;
}
