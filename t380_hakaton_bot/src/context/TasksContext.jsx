import React, { createContext, useContext, useState, useEffect } from 'react';
import { maxBridge } from '../utils/maxBridge';

const TasksContext = createContext();

export const useTasks = () => {
  const context = useContext(TasksContext);
  if (!context) {
    throw new Error('useTasks must be used within TasksProvider');
  }
  return context;
};

export const TasksProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [completedTasks, setCompletedTasks] = useState([]);
  const [missedTasks, setMissedTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [loadedTasks, loadedCompleted, loadedMissed] = await Promise.all([
          maxBridge.get('tasks'),
          maxBridge.get('completedTasks'),
          maxBridge.get('missedTasks'),
        ]);
        
        setTasks(loadedTasks || []);
        setCompletedTasks(loadedCompleted || []);
        setMissedTasks(loadedMissed || []);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadData();
  }, []);

  useEffect(() => {
    if (!isLoading) {
      maxBridge.set('tasks', tasks);
    }
  }, [tasks, isLoading]);

  useEffect(() => {
    if (!isLoading) {
      maxBridge.set('completedTasks', completedTasks);
    }
  }, [completedTasks, isLoading]);

  useEffect(() => {
    if (!isLoading) {
      maxBridge.set('missedTasks', missedTasks);
    }
  }, [missedTasks, isLoading]);

  const addTask = (task) => {
    const newTask = {
      ...task,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
    };
    setTasks(prev => [...prev, newTask]);
    return newTask;
  };

  const updateTask = (id, updates) => {
    setTasks(prev => prev.map(task => 
      task.id === id ? { ...task, ...updates } : task
    ));
  };

  const deleteTask = (id) => {
    setTasks(prev => prev.filter(task => task.id !== id));
  };

  const completeTask = (taskId, date) => {
    const task = tasks.find(t => t.id === taskId);
    if (task) {
      const completion = {
        taskId,
        date: date || new Date().toISOString().split('T')[0],
        completedAt: new Date().toISOString(),
      };
      setCompletedTasks(prev => [...prev, completion]);
    }
  };

  const uncompleteTask = (taskId, date) => {
    setCompletedTasks(prev => 
      prev.filter(c => !(c.taskId === taskId && c.date === date))
    );
  };

  const isTaskCompleted = (taskId, date) => {
    const dateStr = date || new Date().toISOString().split('T')[0];
    return completedTasks.some(
      c => c.taskId === taskId && c.date === dateStr
    );
  };

  const isTaskMissed = (taskId, date) => {
    const dateStr = date || new Date().toISOString().split('T')[0];
    return missedTasks.some(
      m => m.taskId === taskId && m.date === dateStr
    );
  };

  const markTaskMissed = (taskId, date) => {
    const task = tasks.find(t => t.id === taskId);
    if (task) {
      const dateStr = date || new Date().toISOString().split('T')[0];
      setMissedTasks(prev => {
        // Переключаем состояние - если уже есть, удаляем, если нет - добавляем
        const exists = prev.some(m => m.taskId === taskId && m.date === dateStr);
        if (exists) {
          return prev.filter(m => !(m.taskId === taskId && m.date === dateStr));
        } else {
          const missed = {
            taskId,
            date: dateStr,
            missedAt: new Date().toISOString(),
          };
          return [...prev, missed];
        }
      });
    }
  };

  const unmarkTaskMissed = (taskId, date) => {
    const dateStr = date || new Date().toISOString().split('T')[0];
    setMissedTasks(prev => 
      prev.filter(m => !(m.taskId === taskId && m.date === dateStr))
    );
  };

  const rescheduleTask = (taskId, newDate, newTime) => {
    const task = tasks.find(t => t.id === taskId);
    if (task && task.type === 'one-time') {
      const [hours, minutes] = newTime.split(':');
      const newDateTime = new Date(newDate);
      newDateTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      
      updateTask(taskId, {
        startTime: newDateTime.toISOString(),
        endTime: task.endTime ? (() => {
          const duration = new Date(task.endTime) - new Date(task.startTime);
          const newEndTime = new Date(newDateTime.getTime() + duration);
          return newEndTime.toISOString();
        })() : newDateTime.toISOString(),
      });
      
      const taskDate = new Date(task.startTime).toISOString().split('T')[0];
      unmarkTaskMissed(taskId, taskDate);
    }
  };

  const getTasksForDate = (date) => {
    const dateStr = typeof date === 'string' ? date : date.toISOString().split('T')[0];
    return tasks.filter(task => {
      if (task.type === 'one-time') {
        const taskDate = task.startTime.split('T')[0];
        return taskDate === dateStr;
      } else if (task.type === 'recurring') {
        const startDate = new Date(task.startDate);
        const dayOfWeek = new Date(dateStr).getDay();
        const weekNumber = getWeekNumber(new Date(dateStr), startDate);
        
        if (weekNumber > task.cycleWeeks) return false;
        
        return task.daysOfWeek.includes(dayOfWeek);
      }
      return false;
    });
  };

  const getWeekNumber = (currentDate, startDate) => {
    const diffTime = currentDate - startDate;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return Math.floor(diffDays / 7) + 1;
  };

  const getCurrentTask = () => {
    const now = new Date();
    const allTasks = getAllTasksForDate(now);
    const dateStr = now.toISOString().split('T')[0];
    const uncompletedTasks = allTasks.filter(task => !isTaskCompleted(task.id, dateStr));
    
    return uncompletedTasks.find(task => {
      const start = new Date(task.startTime);
      const end = new Date(task.endTime || task.startTime);
      return now >= start && now <= end;
    });
  };

  const getNextTask = () => {
    const now = new Date();
    const allTasks = getAllTasksForDate(now);
    const dateStr = now.toISOString().split('T')[0];
    const uncompletedTasks = allTasks.filter(task => !isTaskCompleted(task.id, dateStr));
    
    const upcoming = uncompletedTasks
      .filter(task => {
        const start = new Date(task.startTime);
        return start > now;
      })
      .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));
    
    return upcoming[0];
  };

  const checkAndMarkMissedTasks = () => {
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    
    tasks.forEach(task => {
      if (task.type === 'one-time') {
        const taskDate = new Date(task.startTime).toISOString().split('T')[0];
        const taskEnd = new Date(task.endTime || task.startTime);
        
        if (taskDate === today && now > taskEnd && 
            !isTaskCompleted(task.id, taskDate) && 
            !isTaskMissed(task.id, taskDate)) {
          markTaskMissed(task.id, taskDate);
        }
      }
    });
  };

  const getAllTasksForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    const result = [];
    
    tasks.forEach(task => {
      if (task.type === 'one-time') {
        const taskDate = task.startTime.split('T')[0];
        if (taskDate === dateStr) {
          result.push(task);
        }
      } else if (task.type === 'recurring') {
        const startDate = new Date(task.startDate);
        const jsDayOfWeek = date.getDay();
        const dayOfWeek = jsDayOfWeek === 0 ? 6 : jsDayOfWeek - 1;
        const weekNumber = getWeekNumber(date, startDate);
        
        if (weekNumber <= task.cycleWeeks && task.daysOfWeek.includes(dayOfWeek)) {
          const [hours, minutes] = task.time.split(':');
          const taskDateTime = new Date(date);
          taskDateTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);
          
          result.push({
            ...task,
            startTime: taskDateTime.toISOString(),
            endTime: task.endTime ? (() => {
              const [endHours, endMinutes] = task.endTime.split(':');
              const endDateTime = new Date(date);
              endDateTime.setHours(parseInt(endHours), parseInt(endMinutes), 0, 0);
              return endDateTime.toISOString();
            })() : taskDateTime.toISOString(),
          });
        }
      }
    });
    
    return result.sort((a, b) => new Date(a.startTime) - new Date(b.startTime));
  };

  const getThreadStrength = () => {
    const period = localStorage.getItem('threadPeriod') || 'month';
    let daysCount = 30; // месяц по умолчанию
    
    if (period === 'day') {
      daysCount = 1;
    } else if (period === 'week') {
      daysCount = 7;
    } else if (period === 'month') {
      daysCount = 30;
    }

    const dates = [];
    for (let i = 0; i < daysCount; i++) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      dates.push(date.toISOString().split('T')[0]);
    }

    let completed = 0;
    let total = 0;

    dates.forEach(date => {
      const tasksForDate = getAllTasksForDate(new Date(date));
      total += tasksForDate.length;
      tasksForDate.forEach(task => {
        if (isTaskCompleted(task.id, date)) {
          completed++;
        }
      });
    });

    return total > 0 ? (completed / total) * 100 : 100;
  };

  useEffect(() => {
    checkAndMarkMissedTasks();
    const interval = setInterval(checkAndMarkMissedTasks, 60000);
    return () => clearInterval(interval);
  }, [tasks]);

  const [updateTrigger, setUpdateTrigger] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => {
      setUpdateTrigger(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <TasksContext.Provider value={{
      tasks,
      completedTasks,
      addTask,
      updateTask,
      deleteTask,
      completeTask,
      uncompleteTask,
      isTaskCompleted,
      isTaskMissed,
      markTaskMissed,
      unmarkTaskMissed,
      rescheduleTask,
      getTasksForDate,
      getCurrentTask,
      getNextTask,
      getAllTasksForDate,
      getThreadStrength,
    }}>
      {children}
    </TasksContext.Provider>
  );
};

