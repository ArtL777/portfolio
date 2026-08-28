import React, { useState } from 'react';
import { useTasks } from '../context/TasksContext';
import './TaskForm.css';

const TaskForm = ({ onClose, taskToEdit = null, initialDate = null }) => {
  const { addTask, updateTask } = useTasks();
  const [taskType, setTaskType] = useState(taskToEdit?.type || 'one-time');
  const [name, setName] = useState(taskToEdit?.name || '');
  const [startDate, setStartDate] = useState(
    taskToEdit?.startTime
      ? new Date(taskToEdit.startTime).toISOString().split('T')[0]
      : initialDate
        ? new Date(initialDate).toISOString().split('T')[0]
        : new Date().toISOString().split('T')[0]
  );
  const [startTime, setStartTime] = useState(
    taskToEdit?.startTime
      ? new Date(taskToEdit.startTime).toTimeString().slice(0, 5)
      : '09:00'
  );
  const [endTime, setEndTime] = useState(
    taskToEdit?.endTime
      ? new Date(taskToEdit.endTime).toTimeString().slice(0, 5)
      : ''
  );
  const [location, setLocation] = useState(taskToEdit?.location || '');
  const [importance, setImportance] = useState(taskToEdit?.importance || 'medium');
  const [comment, setComment] = useState(taskToEdit?.comment || '');
  const [daysOfWeek, setDaysOfWeek] = useState(taskToEdit?.daysOfWeek || []);
  const [cycleWeeks, setCycleWeeks] = useState(taskToEdit?.cycleWeeks || 1);
  const [startDateRecurring, setStartDateRecurring] = useState(
    taskToEdit?.startDate
      ? new Date(taskToEdit.startDate).toISOString().split('T')[0]
      : new Date().toISOString().split('T')[0]
  );

  const days = [
    { value: 0, label: 'Пн' },
    { value: 1, label: 'Вт' },
    { value: 2, label: 'Ср' },
    { value: 3, label: 'Чт' },
    { value: 4, label: 'Пт' },
    { value: 5, label: 'Сб' },
    { value: 6, label: 'Вс' },
  ];

  const toggleDay = (day) => {
    setDaysOfWeek(prev =>
      prev.includes(day)
        ? prev.filter(d => d !== day)
        : [...prev, day]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!name.trim()) {
      alert('Пожалуйста, укажите название дела');
      return;
    }

    if (taskType === 'one-time') {
      const startDateTime = new Date(`${startDate}T${startTime}`);
      const endDateTime = endTime
        ? new Date(`${startDate}T${endTime}`)
        : new Date(startDateTime.getTime() + 60 * 60 * 1000); // +1 час по умолчанию

      const task = {
        type: 'one-time',
        name: name.trim(),
        startTime: startDateTime.toISOString(),
        endTime: endDateTime.toISOString(),
        location: location.trim() || undefined,
        importance: importance,
        comment: comment.trim() || undefined,
      };

      if (taskToEdit) {
        updateTask(taskToEdit.id, task);
      } else {
        addTask(task);
      }
    } else {
      if (daysOfWeek.length === 0) {
        alert('Пожалуйста, выберите хотя бы один день недели');
        return;
      }

      const task = {
        type: 'recurring',
        name: name.trim(),
        startDate: startDateRecurring,
        time: startTime,
        endTime: endTime || undefined,
        daysOfWeek: daysOfWeek.sort(),
        cycleWeeks: cycleWeeks,
        location: location.trim() || undefined,
        importance: importance,
        comment: comment.trim() || undefined,
      };

      if (taskToEdit) {
        updateTask(taskToEdit.id, task);
      } else {
        addTask(task);
      }
    }

    onClose();
  };

  return (
    <div className="task-form-overlay" onClick={onClose}>
      <div className="task-form card" onClick={(e) => e.stopPropagation()}>
        <div className="form-header">
          <h2>{taskToEdit ? 'Редактировать дело' : 'Добавить дело'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label">Тип дела</label>
            <select
              className="select"
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
            >
              <option value="one-time">Одноразовое</option>
              <option value="recurring">Повторяющееся</option>
            </select>
          </div>

          <div className="form-group">
            <label className="label">Название дела *</label>
            <input
              type="text"
              className="input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          {taskType === 'one-time' ? (
            <>
              <div className="form-group">
                <label className="label">Дата *</label>
                <input
                  type="date"
                  className="input"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="label">Время начала *</label>
                  <input
                    type="time"
                    className="input"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="label">Время окончания</label>
                  <input
                    type="time"
                    className="input"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                  />
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="form-group">
                <label className="label">Дата начала цикла *</label>
                <input
                  type="date"
                  className="input"
                  value={startDateRecurring}
                  onChange={(e) => setStartDateRecurring(e.target.value)}
                  required
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="label">Время начала *</label>
                  <input
                    type="time"
                    className="input"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="label">Время окончания</label>
                  <input
                    type="time"
                    className="input"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                  />
                </div>
              </div>
              <div className="form-group">
                <label className="label">Дни недели *</label>
                <div className="days-selector">
                  {days.map(day => (
                    <button
                      key={day.value}
                      type="button"
                      className={`day-button ${daysOfWeek.includes(day.value) ? 'selected' : ''}`}
                      onClick={() => toggleDay(day.value)}
                    >
                      {day.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="form-group">
                <label className="label">Цикл (недель) *</label>
                <select
                  className="select"
                  value={cycleWeeks}
                  onChange={(e) => setCycleWeeks(parseInt(e.target.value))}
                >
                  <option value={1}>1 неделя</option>
                  <option value={2}>2 недели</option>
                  <option value={3}>3 недели</option>
                  <option value={4}>4 недели</option>
                </select>
              </div>
            </>
          )}

          <div className="form-group">
            <label className="label">Локация</label>
            <input
              type="text"
              className="input"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Например: ВУЗ, Спортзал"
            />
          </div>

          <div className="form-group">
            <label className="label">Уровень важности</label>
            <select
              className="select"
              value={importance}
              onChange={(e) => setImportance(e.target.value)}
            >
              <option value="low">Низкая</option>
              <option value="medium">Средняя</option>
              <option value="high">Высокая</option>
            </select>
          </div>

          <div className="form-group">
            <label className="label">Комментарий</label>
            <textarea
              className="input textarea"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows="3"
              placeholder="Дополнительная информация..."
            />
          </div>

          <div className="form-actions">
            <button type="button" className="button button-secondary" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="button">
              {taskToEdit ? 'Сохранить' : 'Добавить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskForm;

