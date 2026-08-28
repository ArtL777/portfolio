import React, { useState } from 'react';
import { MaxUI } from '@maxhub/max-ui';
import { ThemeProvider } from './context/ThemeContext';
import { TasksProvider } from './context/TasksContext';
import MainPage from './components/MainPage';
import CalendarPage from './components/CalendarPage';
import SettingsPage from './components/SettingsPage';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('main');

  return (
    <MaxUI>
      <ThemeProvider>
        <TasksProvider>
          <div className="app">
            <div className="app-content">
              {currentPage === 'main' && <MainPage />}
              {currentPage === 'calendar' && <CalendarPage />}
              {currentPage === 'settings' && <SettingsPage />}
            </div>
            <Navigation currentPage={currentPage} setCurrentPage={setCurrentPage} />
          </div>
        </TasksProvider>
      </ThemeProvider>
    </MaxUI>
  );
}

export default App;

