import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { useTasks } from '../context/TasksContext';
import { maxBridge } from '../utils/maxBridge';
import './SettingsPage.css';

const SettingsPage = () => {
  const { theme, toggleTheme } = useTheme();
  const { getThreadStrength } = useTasks();
  
  const [notifications, setNotifications] = useState({
    enabled: true,
    beforeTask: 15,
    missedTask: true,
    inactiveDays: 3,
  });

  const [threadPeriod, setThreadPeriod] = useState('month');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const [loadedNotifications, loadedPeriod] = await Promise.all([
          maxBridge.get('notifications'),
          maxBridge.get('threadPeriod'),
        ]);
        
        if (loadedNotifications) {
          setNotifications(loadedNotifications);
        }
        if (loadedPeriod) {
          setThreadPeriod(loadedPeriod);
        }
      } catch (error) {
        console.error('Error loading settings:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadSettings();
  }, []);

  const [threadStrengthValue, setThreadStrengthValue] = useState(0);
  
  useEffect(() => {
    const updateStrength = () => {
      setThreadStrengthValue(getThreadStrength());
    };
    updateStrength();
    const interval = setInterval(updateStrength, 1000);
    return () => clearInterval(interval);
  }, [threadPeriod, getThreadStrength]);

  useEffect(() => {
    if (!isLoading) {
      maxBridge.set('notifications', notifications);
    }
  }, [notifications, isLoading]);

  useEffect(() => {
    if (!isLoading) {
      maxBridge.set('threadPeriod', threadPeriod);
    }
  }, [threadPeriod, isLoading]);

  const handleNotificationChange = (key, value) => {
    setNotifications(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  return (
    <div className="settings-page">
      <h1 className="page-title">Настройки</h1>

      <div className="settings-section card">
        <h2 className="section-title">Тема приложения</h2>
        <div className="theme-selector">
          <button
            className={`theme-option ${theme === 'light' ? 'active' : ''}`}
            onClick={() => theme !== 'light' && toggleTheme()}
          >
            <span className="theme-icon">☀️</span>
            <span>Светлая</span>
          </button>
          <button
            className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
            onClick={() => theme !== 'dark' && toggleTheme()}
          >
            <span className="theme-icon">🌙</span>
            <span>Тёмная</span>
          </button>
        </div>
      </div>

      <div className="settings-section card">
        <h2 className="section-title">Уведомления</h2>
        
        <div className="setting-item">
          <div className="setting-label">
            <label>Включить уведомления</label>
            <span className="setting-description">
              Получать напоминания о предстоящих делах
            </span>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={notifications.enabled}
              onChange={(e) => handleNotificationChange('enabled', e.target.checked)}
            />
            <span className="slider"></span>
          </label>
        </div>

        {notifications.enabled && (
          <>
            <div className="setting-item">
              <div className="setting-label">
                <label>Напоминать за (минут)</label>
                <span className="setting-description">
                  За сколько минут до начала дела отправлять напоминание
                </span>
              </div>
              <select
                className="select setting-select"
                value={notifications.beforeTask}
                onChange={(e) => handleNotificationChange('beforeTask', parseInt(e.target.value))}
              >
                <option value={5}>5 минут</option>
                <option value={10}>10 минут</option>
                <option value={15}>15 минут</option>
                <option value={30}>30 минут</option>
                <option value={60}>1 час</option>
              </select>
            </div>

            <div className="setting-item">
              <div className="setting-label">
                <label>Уведомлять о пропущенных делах</label>
                <span className="setting-description">
                  Получать уведомления о невыполненных делах
                </span>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={notifications.missedTask}
                  onChange={(e) => handleNotificationChange('missedTask', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-label">
                <label>Уведомлять о неактивности</label>
                <span className="setting-description">
                  Уведомлять, если давно не выполнялись дела
                </span>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={notifications.inactiveDays > 0}
                  onChange={(e) => handleNotificationChange('inactiveDays', e.target.checked ? 3 : 0)}
                />
                <span className="slider"></span>
              </label>
            </div>

            {notifications.inactiveDays > 0 && (
              <div className="setting-item">
                <div className="setting-label">
                  <label>Дней без активности</label>
                  <span className="setting-description">
                    Через сколько дней без выполнения дел отправлять уведомление
                  </span>
                </div>
                <select
                  className="select setting-select"
                  value={notifications.inactiveDays}
                  onChange={(e) => handleNotificationChange('inactiveDays', parseInt(e.target.value))}
                >
                  <option value={1}>1 день</option>
                  <option value={2}>2 дня</option>
                  <option value={3}>3 дня</option>
                  <option value={7}>7 дней</option>
                </select>
              </div>
            )}
          </>
        )}
      </div>

      <div className="settings-section card">
        <h2 className="section-title">Плексус</h2>
        
        <div className="setting-item">
          <div className="setting-label">
            <label>Период расчета</label>
            <span className="setting-description">
              За какой период рассчитывается прочность нити
            </span>
          </div>
          <select
            className="select setting-select"
            value={threadPeriod}
            onChange={(e) => {
              setThreadPeriod(e.target.value);
            }}
          >
            <option value="day">День</option>
            <option value="week">Неделя</option>
            <option value="month">Месяц</option>
          </select>
        </div>
        
        <div className="setting-item">
          <div className="setting-label">
            <label>Текущая прочность</label>
            <span className="setting-description">
              Прочность нити за выбранный период
            </span>
          </div>
          <div className="thread-strength-preview">
            <span className="thread-strength-value">{Math.round(threadStrengthValue)}%</span>
          </div>
        </div>
      </div>

      <div className="settings-section card">
        <h2 className="section-title">О приложении</h2>
        <p className="about-text">
          Плексус — приложение для управления делами и повышения личной эффективности.
          Выполняйте дела, чтобы сплести крепкую нить из ниточек!
        </p>
        <p className="version-text">Версия 1.0.0</p>
      </div>
    </div>
  );
};

export default SettingsPage;

