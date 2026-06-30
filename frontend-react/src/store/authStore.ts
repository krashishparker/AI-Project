import { create } from 'zustand';
import { User } from '@/types';
import { authService } from '@/services/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: authService.getUser(),
  isAuthenticated: authService.isAuthenticated(),
  
  login: async (username: string, password: string) => {
    const response = await authService.login({ username, password });
    set({ user: response.user, isAuthenticated: true });
  },
  
  register: async (email: string, username: string, password: string, fullName?: string) => {
    await authService.register({ email, username, password, full_name: fullName });
  },
  
  logout: () => {
    authService.logout();
    set({ user: null, isAuthenticated: false });
  },
  
  checkAuth: () => {
    const user = authService.getUser();
    set({ user, isAuthenticated: !!user });
  },
}));
