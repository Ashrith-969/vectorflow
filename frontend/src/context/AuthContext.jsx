import { createContext, useContext, useState, useCallback } from 'react';
import { useMutation } from '@apollo/client';
import { LOGIN, REGISTER } from '../graphql/mutations';
import { setToken } from '../apollo/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loginMutation] = useMutation(LOGIN);
  const [registerMutation] = useMutation(REGISTER);

  const login = useCallback(async (email, password) => {
    const { data } = await loginMutation({
      variables: { input: { email, password } },
    });
    setToken(data.login.token);
    setUser(data.login.user);
    return data.login.user;
  }, [loginMutation]);

  const register = useCallback(async (email, password) => {
    const { data } = await registerMutation({
      variables: { input: { email, password } },
    });
    setToken(data.register.token);
    setUser(data.register.user);
    return data.register.user;
  }, [registerMutation]);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const hasRole = useCallback((...roles) => {
    return user && roles.includes(user.role);
  }, [user]);

  return (
    <AuthContext.Provider value={{ user, login, register, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
