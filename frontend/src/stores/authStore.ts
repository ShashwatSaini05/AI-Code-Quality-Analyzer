import { create } from 'zustand';
import type { User } from '../types';

// Default user — no login required
const DEFAULT_USER: User = {
  id: 'default-user',
  email: 'developer@codesage.ai',
  username: 'Developer',
  full_name: 'CodeSage Developer',
  role: 'admin',
  auth_provider: 'local',
  is_active: true,
  is_verified: true,
  created_at: new Date().toISOString(),
};

interface AuthState {
  user: User;
  isAuthenticated: boolean;
}

export const useAuthStore = create<AuthState>(() => ({
  user: DEFAULT_USER,
  isAuthenticated: true,
}));
