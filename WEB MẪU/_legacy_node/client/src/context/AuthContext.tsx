import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { api, getToken, setToken, removeToken } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (credentials: { tenDangNhap: string; matKhau: string }) => Promise<User>;
  register: (payload: { hoTen: string; soDienThoai: string; tenDangNhap: string; matKhau: string }) => Promise<User>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(getToken());
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    const currentToken = getToken();
    if (!currentToken) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const data = await api.getMe();
      setUser(data);
    } catch (error) {
      console.error('Không thể xác thực phiên:', error);
      removeToken();
      setTokenState(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (credentials: { tenDangNhap: string; matKhau: string }) => {
    const res = await api.login(credentials);
    setToken(res.token);
    setTokenState(res.token);
    setUser(res.user);
    return res.user;
  };

  const register = async (payload: { hoTen: string; soDienThoai: string; tenDangNhap: string; matKhau: string }) => {
    const res = await api.register(payload);
    setToken(res.token);
    setTokenState(res.token);
    setUser(res.user);
    return res.user;
  };

  const logout = () => {
    removeToken();
    setTokenState(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
