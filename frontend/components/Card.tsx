import React from 'react';

interface CardProps {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  headerAction?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ title, icon, children, className = '', headerAction }) => {
  return (
    <div className={`glass-panel rounded-md flex flex-col ${className}`}>
      <div className="px-4 py-3 border-b border-scada-border flex items-center justify-between bg-white/5">
        <div className="flex items-center gap-3">
            {icon && <span className="text-scada-accent opacity-80">{icon}</span>}
            <h2 className="text-sm font-bold text-white tracking-widest uppercase">{title}</h2>
        </div>
        {headerAction && <div>{headerAction}</div>}
      </div>
      
      <div className="p-4 flex-1">
        {children}
      </div>
    </div>
  );
};