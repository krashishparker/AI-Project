import { AuthResponse, LoginCredentials, RegisterData, User } from '@/types';

// Hardcoded user credentials
const HARDCODED_USER: User = {
  id: 1,
  email: 'admin@example.com',
  username: 'admin',
  full_name: 'Admin User',
  is_active: true,
  created_at: new Date().toISOString(),
};

const HARDCODED_CREDENTIALS = {
  username: 'admin',
  password: 'admin123',
};

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    if (credentials.username === HARDCODED_CREDENTIALS.username && 
        credentials.password === HARDCODED_CREDENTIALS.password) {
      const token = 'hardcoded-token-' + Date.now();
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(HARDCODED_USER));
      return {
        access_token: token,
        token_type: 'bearer',
        user: HARDCODED_USER,
      };
    }

    throw new Error('Invalid username or password');
  },

  async register(data: RegisterData): Promise<User> {
    // Registration is disabled with hardcoded auth
    throw new Error('Registration is disabled. Please use the hardcoded credentials.');
  },

  async getCurrentUser(): Promise<User> {
    const user = this.getUser();
    if (!user) {
      throw new Error('Not authenticated');
    }
    return user;
  },

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getToken(): string | null {
    return localStorage.getItem('token');
  },

  getUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};
