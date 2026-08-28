import React, { createContext, useContext, useState, useEffect } from 'react';
import { maxBridge } from '../utils/maxBridge';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadTheme = async () => {
      try {
        const saved = await maxBridge.get('theme');
        setTheme(saved || 'light');
      } catch (error) {
        console.error('Error loading theme:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadTheme();
  }, []);

  useEffect(() => {
    if (!isLoading) {
      document.body.className = `${theme}-theme`;
      maxBridge.set('theme', theme);
    }
  }, [theme, isLoading]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

