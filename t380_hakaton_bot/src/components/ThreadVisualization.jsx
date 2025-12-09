import React, { useEffect, useState } from 'react';
import './ThreadVisualization.css';

const ThreadVisualization = ({ strength }) => {
  const [animatedStrength, setAnimatedStrength] = useState(0);
  
  useEffect(() => {
    const duration = 500;
    const startTime = Date.now();
    const startStrength = animatedStrength;
    const targetStrength = strength;
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const current = startStrength + (targetStrength - startStrength) * easeOutCubic;
      
      setAnimatedStrength(current);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    animate();
  }, [strength]);

  const segments = 30;
  const segmentAngle = 360 / segments;
  
  const getSegmentColor = (index) => {
    const segmentProgress = (animatedStrength / 100) * segments;
    const segmentIndex = segments - index - 1;
    
    if (segmentIndex >= segmentProgress) {
      return 'transparent';
    }
    
    const segmentStrength = (segmentIndex / segments) * 100;
    if (segmentStrength >= 80) return '#4caf50';
    if (segmentStrength >= 50) return '#ff9800';
    if (segmentStrength >= 20) return '#ff5722';
    return '#9e9e9e';
  };

  return (
    <div className="thread-container card">
      <h2 className="thread-title">Плексус</h2>
      
      <div className="thread-visualization-wrapper">
        <div className="thread-circle">
          <svg viewBox="0 0 200 200" className="thread-svg">
            <defs>
              <linearGradient id="threadGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#4caf50" />
                <stop offset="50%" stopColor="#ff9800" />
                <stop offset="100%" stopColor="#ff5722" />
              </linearGradient>
            </defs>
            {Array.from({ length: segments }).map((_, index) => {
              const angle = (index * segmentAngle - 90) * (Math.PI / 180);
              const x1 = 100 + 80 * Math.cos(angle);
              const y1 = 100 + 80 * Math.sin(angle);
              const x2 = 100 + 90 * Math.cos(angle);
              const y2 = 100 + 90 * Math.sin(angle);
              const color = getSegmentColor(index);
              
              return (
                <line
                  key={index}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke={color}
                  strokeWidth="3"
                  strokeLinecap="round"
                  className="thread-segment-line"
                />
              );
            })}
          </svg>
          
          <div className="thread-center">
            <div className="thread-percentage">
              {Math.round(animatedStrength)}%
            </div>
            <div className="thread-label">Прочность</div>
          </div>
        </div>
      </div>
      
      <div className="thread-stats">
        <div className="thread-legend">
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#4caf50' }}></div>
            <span>Крепкая (80-100%)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#ff9800' }}></div>
            <span>Средняя (50-79%)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#ff5722' }}></div>
            <span>Слабая (20-49%)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#9e9e9e' }}></div>
            <span>Повреждена (&lt;20%)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThreadVisualization;
