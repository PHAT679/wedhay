import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, UserRole, VALID_USER_ROLES } from '../types';
import { mockUsers } from '../data/mockData';
import { api, getAuthToken, setAuthToken, removeAuthToken } from '../services/api';

interface AuthContextType {
  currentUser: User;
  authenticated: boolean;
  loading: boolean;
  switchUser: (role: UserRole) => void;
  loginWithEmail: (email: string, password: string) => Promise<void>;
  logout: () => void;
  allUsers: User[];
}
const AuthContext = createContext<AuthContextType | undefined>(undefined);
const guest: User = { id: '', email: '', fullName: '', department: '', role: 'BTC' };
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User>(guest);
  const [loading, setLoading] = useState(true);
  const acceptUser = (user: User) => {
    if (!VALID_USER_ROLES.includes(user.role) || user.isActive === false) throw new Error('Tài khoản chưa được phân quyền');
    setCurrentUser({ ...user, department: user.department || '' });
  };
  useEffect(() => {
    let active = true;
    if (!getAuthToken()) { setLoading(false); return; }
    api.getMe().then(result => { if (active) acceptUser(result.data); })
      .catch(() => { if (active) removeAuthToken(); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  const logout = () => { removeAuthToken(); setCurrentUser(guest); };
  const loginWithEmail = async (email: string, password: string) => {
    const { data } = await api.login(email.trim(), password);
    acceptUser(data.user);
    setAuthToken(data.token);
  };
  const switchUser = (role: UserRole) => {
    const user = mockUsers.find(u => u.role === role);
    logout();
    window.location.assign(`/login${user ? `?email=${encodeURIComponent(user.email)}` : ''}`);
  };
  return <AuthContext.Provider value={{ currentUser, authenticated: Boolean(currentUser.id), loading, switchUser, loginWithEmail, logout, allUsers: mockUsers }}>{children}</AuthContext.Provider>;
};
export const useAuth = () => {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used within AuthProvider');
  return value;
};
