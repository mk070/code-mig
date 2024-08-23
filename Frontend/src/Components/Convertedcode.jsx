import { useState, useRef, useEffect } from 'react';
import CloseIcon from '@mui/icons-material/Close';
import MinimizeIcon from '@mui/icons-material/Minimize';
import MaximizeIcon from '@mui/icons-material/Maximize';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loader from '../layout/Loader';


export const Convertedcode = ({ code, onRun, SourceLanguage, TargetLanguage,onRunComplete }) => {
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);
  const codeContainerRef = useRef(null);
  const lineNumbersRef = useRef(null);
  const [loading, setLoading] = useState(false); // State for loading
  const [mode, setMode] = useState('compile'); // Set default mode to 'compile'

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

  const handleRun = async () => {
    setLoading(true);  // Start the loader
    setMode('compile'); // Set mode to compile

    console.log("heloo")
    try {
      const formData = new FormData();
      console.log("TargetLanguage : ",TargetLanguage)
      // Determine the correct file extension based on SourceLanguage
      let fileExtension = '';
      switch (TargetLanguage.value.toLowerCase()) {
        case 'cobol':
          fileExtension = 'cbl';
          break;
        case 'python':
          fileExtension = 'py';
          break;
        case 'java':
          fileExtension = 'java';
          break;
        case '.net':
          fileExtension = 'cs';
          break;
        case 'pyspark':
          fileExtension = 'py';
          break;
        case 'sql':
          fileExtension = 'sql';
          break;
        default:
          fileExtension = 'txt'; // default if no match
      }
  
      const mainFileName = `main.${fileExtension}`;
  
      // If code is present, save it as a file in the backend
      if (code.trim()) {
        const blob = new Blob([code], { type: 'text/plain' });
        const codeFile = new File([blob], mainFileName);
        formData.append('files', codeFile);
      }
  
      formData.append('sourcelanguage', SourceLanguage.value);
      formData.append('targetlanguage', TargetLanguage.value);
      formData.append('main_file_name', mainFileName); // Add the main_file_name to the form data
  

      const response = await axios.post('http://127.0.0.1:8000/compile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
  
      console.log('Response from backend:', response.data);
  
      if (response.status === 200 && response.data.output) {
        toast.success('Code executed successfully!');
        // Ensure onRunComplete is defined and passed correctly
        if (onRunComplete) {
          onRunComplete(response.data.output); // Pass the output to the parent component
        }
      } else if (response.data.error) {
        toast.error(`Error: ${response.data.error}`);
      } else {
        toast.error('An unexpected error occurred.');
      }
    } catch (error) {
      console.error('Error running code:', error);
      toast.error('An error occurred while running the code.');
    } finally {
      setLoading(false);  // Stop the loader

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
      <div className="relative h-80 bg-gray-900 rounded-b-md shadow-lg overflow-hidden">
        <div className="flex">
          <div
            ref={lineNumbersRef}
            className="w-10 bg-gray-800 h-screen text-gray-400 text-right p-2 font-mono text-sm border-r border-gray-700 overflow-hidden h-64 editor-scrollbar"
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
            className="w-full pl-4 pr-4 py-4 h-screen bg-gray-900 text-white border-none font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 resize-none overflow-auto h-64 editor-scrollbar"
            placeholder="Converted code will appear here..."
            style={{ lineHeight: '1.5rem' ,height:'320px'}}
          ></textarea>
        </div>
      </div>
      <button
        type="button"
        className={`gap-2 flex items-center justify-center text-white text-sm mt-2 w-full p-2.5 ${isButtonDisabled ? 'bg-green-300 cursor-not-allowed' : 'bg-green-600 hover:bg-green-600'} text-sm font-medium rounded-md shadow-sm transition duration-300 ease-in-out p-2`}
        onClick={handleRun}
      >
        <PlayArrowIcon />
        Run
      </button>
      {loading && <Loader mode={mode} />} {/* Show loader when loading */}

    </div>
  );
};
