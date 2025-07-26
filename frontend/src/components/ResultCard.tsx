import React from 'react';
import './ResultCard.css';

interface ResultCardProps {
  filePath: string;
  fileName: string;
  score: number;
}

const ResultCard: React.FC<ResultCardProps> = ({ filePath, fileName, score }) => {
  const displayScore = typeof score === 'number' && !isNaN(score) ? score.toFixed(3) : 'N/A';
  return (
    <div className="result-card">
      <h3>{fileName}</h3>
      <p><strong>Path:</strong> {filePath}</p>
      <p><strong>Score:</strong> {displayScore}</p>
    </div>
  );
};

export default ResultCard;
