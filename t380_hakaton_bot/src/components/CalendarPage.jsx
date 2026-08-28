import React, { useState } from 'react';
import { useTasks } from '../context/TasksContext';
import TaskForm from './TaskForm';
import './CalendarPage.css';

const CalendarPage = () => {
  const { 
    getAllTasksForDate, 
    isTaskCompleted, 
    isTaskMissed,
    completeTask, 
    uncompleteTask,
    markTaskMissed,
    unmarkTaskMissed
  } = useTasks();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const daysInMonth = lastDayOfMonth.getDate();
  const startingDayOfWeek = firstDayOfMonth.getDay();
  const adjustedStartingDay = startingDayOfWeek === 0 ? 6 : startingDayOfWeek - 1;

  const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ];

  const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const getTasksForDay = (day) => {
    const date = new Date(year, month, day);
    return getAllTasksForDate(date);
  };

  const handleDayClick = (day) => {
    const date = new Date(year, month, day);
    setSelectedDate(date);
  };

  const renderCalendarDays = () => {
    const days = [];
    
    for (let i = 0; i < adjustedStartingDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const tasks = getTasksForDay(day);
      const isToday = date.toDateString() === new Date().toDateString();
      const isSelected = selectedDate && date.toDateString() === selectedDate.toDateString();

      days.push(
        <div
          key={day}
          className={`calendar-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}`}
          onClick={() => handleDayClick(day)}
        >
          <div className="day-number">{day}</div>
          {tasks.length > 0 && (
            <div className="day-tasks">
              <span className="tasks-count">{tasks.length}</span>
            </div>
          )}
        </div>
      );
    }

    return days;
  };

  const selectedDateTasks = selectedDate ? getAllTasksForDate(selectedDate) : [];

  return (
    <div className="calendar-page">
      <div className="calendar-header">
        <h1 className="page-title">Календарь</h1>
        <div className="calendar-controls">
          <button className="button button-small" onClick={goToPreviousMonth}>
            ←
          </button>
          <h2 className="month-year">
            {monthNames[month]} {year}
          </h2>
          <button className="button button-small" onClick={goToNextMonth}>
            →
          </button>
        </div>
        <button className="button button-small" onClick={goToToday}>
          Сегодня
        </button>
      </div>

      <div className="calendar-container card">
        <div className="calendar-weekdays">
          {weekDays.map(day => (
            <div key={day} className="weekday">{day}</div>
          ))}
        </div>
        <div className="calendar-grid">
          {renderCalendarDays()}
        </div>
      </div>

      {selectedDate && (
        <div className="selected-date-tasks card">
          <h3>
            Дела на {selectedDate.toLocaleDateString('ru-RU', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
          </h3>
          {selectedDateTasks.length === 0 ? (
            <p className="no-tasks">Нет дел на этот день</p>
          ) : (
            <div className="tasks-list">
              {selectedDateTasks.map(task => {
                const taskDate = selectedDate.toISOString().split('T')[0];
                const completed = isTaskCompleted(task.id, taskDate);
                const missed = isTaskMissed(task.id, taskDate);
                const startTime = new Date(task.startTime).toLocaleTimeString('ru-RU', {
                  hour: '2-digit',
                  minute: '2-digit',
                });

                return (
                  <div
                    key={task.id}
                    className={`task-item ${completed ? 'completed' : ''} ${missed ? 'missed' : ''}`}
                  >
                    <div className="task-item-content">
                      <div className="task-item-time">{startTime}</div>
                      <div className="task-item-name">{task.name}</div>
                      {task.location && (
                        <div className="task-item-location">📍 {task.location}</div>
                      )}
                      {completed && <div className="task-status-badge completed-badge">✓ Сделано</div>}
                      {missed && !completed && <div className="task-status-badge missed-badge">✗ Не сделано</div>}
                    </div>
                    <div className="task-item-actions">
                      <button
                        className={`complete-button ${completed ? 'checked' : ''}`}
                        onClick={() => {
                          if (completed) {
                            uncompleteTask(task.id, taskDate);
                            if (missed) {
                              unmarkTaskMissed(task.id, taskDate);
                            }
                          } else {
                            completeTask(task.id, taskDate);
                            if (missed) {
                              unmarkTaskMissed(task.id, taskDate);
                            }
                          }
                        }}
                        title={completed ? 'Отменить выполнение' : 'Сделано'}
                      >
                        {completed ? '✓' : '○'}
                      </button>
                      {!completed && (
                        <button
                          className={`missed-button ${missed ? 'active' : ''}`}
                          onClick={() => {
                            markTaskMissed(task.id, taskDate);
                          }}
                          title={missed ? 'Отменить отметку' : 'Не сделано'}
                        >
                          ✗
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
          <button
            className="button add-task-button"
            onClick={() => setShowAddForm(true)}
          >
            + Добавить дело на этот день
          </button>
        </div>
      )}

      {showAddForm && (
        <TaskForm
          onClose={() => setShowAddForm(false)}
          initialDate={selectedDate}
        />
      )}
    </div>
  );
};

export default CalendarPage;

