import React, { useState } from 'react';
import { useTasks } from '../context/TasksContext';
import './CurrentTask.css';

const CurrentTask = ({ task, label, showOnlyWhenStarted = false }) => {
  const { 
    isTaskCompleted, 
    isTaskMissed,
    completeTask,
    unmarkTaskMissed,
    markTaskMissed,
    rescheduleTask 
  } = useTasks();
  const [showReschedule, setShowReschedule] = useState(false);
  const [newDate, setNewDate] = useState('');
  const [newTime, setNewTime] = useState('');

  if (!task) {
    return (
      <div className="current-task card">
        <h3 className="task-label">{label}</h3>
        <p className="no-task">Нет дел</p>
      </div>
    );
  }

  const now = new Date();
  const taskStart = new Date(task.startTime);
  const taskEnd = new Date(task.endTime || task.startTime);
  const taskDate = new Date(task.startTime).toISOString().split('T')[0];
  const isCompleted = isTaskCompleted(task.id, taskDate);
  const isMissed = isTaskMissed(task.id, taskDate);
  const hasStarted = now >= taskStart;
  const hasEnded = now > taskEnd;

  const startTime = taskStart.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  });
  const endTime = task.endTime
    ? taskEnd.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
      })
    : null;

  const showButtons = !showOnlyWhenStarted || hasStarted;

  const handleComplete = () => {
    completeTask(task.id, taskDate);
    if (isMissed) {
      unmarkTaskMissed(task.id, taskDate);
    }
  };

  const handleMissed = () => {
    markTaskMissed(task.id, taskDate);
    if (task.type === 'one-time') {
      setShowReschedule(true);
      setNewDate(new Date(task.startTime).toISOString().split('T')[0]);
      setNewTime(taskStart.toTimeString().slice(0, 5));
    }
  };

  const handleReschedule = () => {
    if (newDate && newTime) {
      rescheduleTask(task.id, newDate, newTime);
      setShowReschedule(false);
    }
  };

  const handleCancelReschedule = () => {
    setShowReschedule(false);
  };

  return (
    <div className={`current-task card ${isCompleted ? 'completed' : ''} ${isMissed ? 'missed' : ''}`}>
      <div className="task-header">
        <h3 className="task-label">{label}</h3>
        {showButtons && !isCompleted && (
          <div className="task-actions">
            <button
              className="complete-button"
              onClick={handleComplete}
              title="Сделано"
            >
              ✓
            </button>
            {hasEnded && (
              <button
                className="missed-button"
                onClick={handleMissed}
                title="Не сделано"
              >
                ✗
              </button>
            )}
          </div>
        )}
        {isCompleted && (
          <div className="task-status completed-status">✓ Сделано</div>
        )}
        {isMissed && !isCompleted && (
          <div className="task-status missed-status">✗ Не сделано</div>
        )}
      </div>
      <h4 className="task-name">{task.name}</h4>
      <div className="task-details">
        <div className="task-time">
          <span className="detail-icon">🕐</span>
          <span>
            {startTime}
            {endTime && ` - ${endTime}`}
          </span>
        </div>
        {task.location && (
          <div className="task-location">
            <span className="detail-icon">📍</span>
            <span>{task.location}</span>
          </div>
        )}
        {task.importance && (
          <div className="task-importance">
            <span className="detail-icon">⭐</span>
            <span>
              {task.importance === 'high' && 'Высокая'}
              {task.importance === 'medium' && 'Средняя'}
              {task.importance === 'low' && 'Низкая'}
            </span>
          </div>
        )}
        {task.comment && (
          <div className="task-comment">
            <span>{task.comment}</span>
          </div>
        )}
      </div>

      {showReschedule && task.type === 'one-time' && (
        <div className="reschedule-form">
          <h4>Перенести дело</h4>
          <div className="form-row">
            <input
              type="date"
              className="input"
              value={newDate}
              onChange={(e) => setNewDate(e.target.value)}
            />
            <input
              type="time"
              className="input"
              value={newTime}
              onChange={(e) => setNewTime(e.target.value)}
            />
          </div>
          <div className="form-actions">
            <button className="button button-secondary" onClick={handleCancelReschedule}>
              Отмена
            </button>
            <button className="button" onClick={handleReschedule}>
              Перенести
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CurrentTask;
