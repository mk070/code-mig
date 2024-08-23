import React, { useState, useRef, useEffect } from 'react';
import UploadButton from './UploadButton';
import CloseIcon from '@mui/icons-material/Close';
import MinimizeIcon from '@mui/icons-material/Minimize';
import MaximizeIcon from '@mui/icons-material/Maximize';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loader from '../layout/Loader';  // Import the Loader component
  
const SourcecodeInput = ({ SourceLanguage, TargetLanguage, onRunComplete }) => {
  const [code, setCode] = useState('');
  const [MainFile, setMainFile] = useState('');
  const [filename, setFilename] = useState(''); 
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);
  const codeContainerRef = useRef(null);
  const lineNumbersRef = useRef(null);
  const [githubLink, setGithubLink] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false); // State for loading
  const [mode, setMode] = useState('compile'); // Set default mode to 'compile'


  useEffect(() => {
    if (code.trim() || githubLink || files.length > 0) {
      setIsButtonDisabled(false);
    } else {
      setIsButtonDisabled(true);
    }
  }, [code, githubLink, files]);

  const handleInputChange = (e) => {
    setCode(e.target.value);
  };

  const getLineNumbers = () => {
    const lines = code.split('\n').length;
    return Array.from({ length: lines }, (_, i) => i + 1).join('\n');
  };

  const syncScroll = () => {
    if (lineNumbersRef.current && codeContainerRef.current) {
      lineNumbersRef.current.scrollTop = codeContainerRef.current.scrollTop;
    }
  };

  const handleFileUpload = (newFiles, mainFileContent) => {
    setFiles(newFiles);
    if (mainFileContent) {
      setCode(mainFileContent);
    }
  };

  const handleGithubLinkChange = (link) => {
    setGithubLink(link);
  };

  const handleMainFile = (name) => {
    setMainFile(name);
  };

  const handleRun = async () => {
    setLoading(true);  // Start the loader
    setMode('compile'); // Set mode to compile

    try {
      const formData = new FormData();

      // Determine the correct file extension based on SourceLanguage
      let fileExtension = '';
      switch (SourceLanguage.value.toLowerCase()) {
        case 'cobol':
          fileExtension = 'cbl';
          break;
        case 'python':
          fileExtension = 'py';
          break;
        case 'java':
          fileExtension = 'java';
          break;
        case 'dotnet':
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

      const database_file_name = '';
      let mainFileName = '';
      if (files.length === 0) {
        mainFileName = `main.${fileExtension}`;
        if (code.trim()) {
          const blob = new Blob([code], { type: 'text/plain' });
          const codeFile = new File([blob], mainFileName);
          formData.append('files', codeFile);
        }      
      } else {
        mainFileName = MainFile;
        formData.append('files', null);
      }

      formData.append('sourcelanguage', SourceLanguage.value);
      formData.append('targetlanguage', TargetLanguage.value);
      formData.append('main_file_name', mainFileName);
      formData.append('database_file_name', database_file_name);

      if (githubLink) {
        formData.append('github_link', githubLink);
      }

      if (files.length > 0) {
        files.forEach((file) => {
          formData.append('files', file);
        });
      }

      const response = await axios.post('http://127.0.0.1:8000/compile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Response from backend:', response.data);

      if (response.status === 200 && response.data.output) {
        toast.success('Code executed successfully!');
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
      setFiles([]);
    }
  };

  return (
    <div className="w-1/2 pr-2">
      <div className="flex items-center justify-between bg-gray-800 text-gray-300 px-4 py-2 rounded-t-md font-mono text-sm">
        <span>{filename ? `File: ${filename}` : 'Source Code'}</span>
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
            className="w-10 h-screen bg-gray-800 text-gray-400 text-right p-2 font-mono text-sm border-r border-gray-700 overflow-hidden h-64 editor-scrollbar"
          >
            <pre>{getLineNumbers()}</pre>
          </div>
          <textarea
            ref={codeContainerRef}
            id="left-code"
            rows="10"
            value={code}
            onChange={handleInputChange}
            onScroll={syncScroll}
            className="w-full pl-4 pr-4 py-4 bg-gray-900 text-white border-none font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 resize-none overflow-auto h-64 editor-scrollbar"
            placeholder="Paste or type your code here..."
            style={{ lineHeight: '1.5rem', height: '320px' }}
          ></textarea>
        </div>
      </div>
      <div className="mt-2 flex items-center justify-center">
        <div className="flex items-center w-1/2">
          <UploadButton onFileUpload={handleFileUpload} MainFile={handleMainFile} onGithubLinkChange={handleGithubLinkChange} />
        </div>
        <button
          type="button"
          className={`ml-2 w-1/2 p-2.5 ${isButtonDisabled ? 'bg-green-300 cursor-not-allowed' : 'bg-green-600'} gap-2 flex items-center justify-center text-white text-sm font-medium rounded-md shadow-sm transition duration-300 ease-in-out`}
          onClick={() => {
            if (!isButtonDisabled) {
              handleRun();
            } else {
              toast.info('Please provide code or upload a file or GitHub link.');
            }
          }}
          disabled={isButtonDisabled}
        >
          <PlayArrowIcon />
          Run
        </button>
      </div>
      {loading && <Loader mode={mode} />} {/* Show loader when loading */}
    </div>
  );
};

export default SourcecodeInput;
