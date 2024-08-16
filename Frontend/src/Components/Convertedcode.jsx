import { useState, useRef, useEffect } from 'react';
import CloseIcon from '@mui/icons-material/Close';
import MinimizeIcon from '@mui/icons-material/Minimize';
import MaximizeIcon from '@mui/icons-material/Maximize';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { toast } from 'react-toastify';

export const Convertedcode = ({ code, onRun }) => {
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);
  const codeContainerRef = useRef(null);
  const lineNumbersRef = useRef(null);

  const getLineNumbers = () => {
    const lines = code.split('\n').length;
    return Array.from({ length: lines }, (_, i) => i + 1).join('\n');
  };

  const syncScroll = () => {
    if (lineNumbersRef.current && codeContainerRef.current) {
      lineNumbersRef.current.scrollTop = codeContainerRef.current.scrollTop;
    }
  };

  useEffect(() => {
    setIsButtonDisabled(code.trim().length === 0);
  }, [code]);

  const handleRunClick = () => {
    if (isButtonDisabled) {
      toast.info('Please convert the code first.', {
        position: 'top-right',
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    } else {
      onRun();  // Trigger the callback to show ConvertedcodeOutput
    }
  };

  return (
    <div className="w-1/2 pl-2">
      <div className="flex items-center justify-between bg-gray-800 text-gray-300 px-4 py-2 rounded-t-md font-mono text-sm">
        <span>Converted Code</span>
        <div className="flex space-x-2">
          <button className="text-gray-400 hover:text-white">
            <MinimizeIcon fontSize="small" />
          </button>
          <button className="text-gray-400 hover:text-white">
            <MaximizeIcon fontSize="small" />
          </button>
          <button className="text-gray-400 hover:text-red-500">
            <CloseIcon fontSize="small" />
          </button>
        </div>
      </div>
      <div className="relative bg-gray-900 rounded-b-md shadow-lg overflow-hidden">
        <div className="flex">
          <div
            ref={lineNumbersRef}
            className="w-10 bg-gray-800 text-gray-400 text-right p-2 font-mono text-sm border-r border-gray-700 overflow-hidden h-64 editor-scrollbar"
          >
            <pre>{getLineNumbers()}</pre>
          </div>
          <textarea
            ref={codeContainerRef}
            id="right-code"
            rows="10"
            value={code}
            readOnly
            onScroll={syncScroll}
            className="w-full pl-4 pr-4 py-4 bg-gray-900 text-white border-none font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 resize-none overflow-auto h-64 editor-scrollbar"
            placeholder="Converted code will appear here..."
            style={{ lineHeight: '1.5rem' }}
          ></textarea>
        </div>
      </div>
      <button
        type="button"
        className={`gap-2 flex items-center justify-center text-white text-sm mt-2 w-full p-2.5 ${isButtonDisabled ? 'bg-green-300 cursor-not-allowed' : 'bg-green-600 hover:bg-green-600'} text-sm font-medium rounded-md shadow-sm transition duration-300 ease-in-out p-2`}
        onClick={handleRunClick}
      >
        <PlayArrowIcon />
        Run
      </button>
    </div>
  );
};
