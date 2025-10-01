import React, { useRef, useState, useEffect } from 'react';
import { Eraser, RotateCcw } from 'lucide-react';

export const DrawingCanvas = ({ onSave, width = 600, height = 600 }) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [context, setContext] = useState(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      setContext(ctx);
      
      // Fill with white background
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, width, height);
    }
  }, [width, height]);

  const startDrawing = (e) => {
    if (!context) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    context.beginPath();
    context.moveTo(x, y);
    setIsDrawing(true);
  };

  const draw = (e) => {
    if (!isDrawing || !context) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    context.lineTo(x, y);
    context.stroke();
  };

  const stopDrawing = () => {
    if (context) {
      context.closePath();
    }
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    if (context) {
      context.fillStyle = '#FFFFFF';
      context.fillRect(0, 0, width, height);
    }
  };

  const saveDrawing = () => {
    if (canvasRef.current && onSave) {
      const dataURL = canvasRef.current.toDataURL('image/png');
      onSave(dataURL);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
        className="border-2 border-gray-300 rounded-lg cursor-crosshair shadow-lg bg-white"
        data-testid="drawing-canvas"
      />
      <div className="flex gap-3">
        <button
          onClick={clearCanvas}
          className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all"
          data-testid="clear-canvas-btn"
        >
          <RotateCcw className="w-4 h-4" />
          Clear
        </button>
        <button
          onClick={saveDrawing}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all"
          data-testid="save-canvas-btn"
        >
          Done
        </button>
      </div>
    </div>
  );
};