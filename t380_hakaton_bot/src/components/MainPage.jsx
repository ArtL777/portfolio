import React, { useState, useEffect } from 'react';
import { useTasks } from '../context/TasksContext';
import ThreadVisualization from './ThreadVisualization';
import CurrentTask from './CurrentTask';
import TaskForm from './TaskForm';
import './MainPage.css';

const MainPage = () => {
  const { getCurrentTask, getNextTask, getThreadStrength } = useTasks();
  const [showAddForm, setShowAddForm] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);
  const [nextTask, setNextTask] = useState(null);
  const [threadStrength, setThreadStrength] = useState(0);
  
  useEffect(() => {
    const updateTasks = () => {
      setCurrentTask(getCurrentTask());
      setNextTask(getNextTask());
      setThreadStrength(getThreadStrength());
    };
    
    updateTasks();
    const interval = setInterval(updateTasks, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="main-page">
      <h1 className="page-title">Плексус</h1>
      
      <ThreadVisualization strength={threadStrength} />
      
      <div className="tasks-section">
        <CurrentTask task={currentTask} label="Текущее дело" showOnlyWhenStarted={true} />
        <CurrentTask task={nextTask} label="Следующее дело" showOnlyWhenStarted={true} />
      </div>

      {showAddForm ? (
        <TaskForm onClose={() => setShowAddForm(false)} />
      ) : (
        <button 
          className="button add-task-button"
          onClick={() => setShowAddForm(true)}
        >
          + Добавить дело
        </button>
      )}
    </div>
  );
};

export default MainPage;

