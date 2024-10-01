import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FaTimes } from 'react-icons/fa';

const FileUploadPopup = ({ onClose, onFileUpload, onGithubLinkChange, MainFile }) => {
  const [githubLink, setGithubLink] = useState('');
  const [repoStructure, setRepoStructure] = useState([]);
  const [files, setFiles] = useState([]);
  const [selectedMainFile, setSelectedMainFile] = useState(null);
  const [selectedDatabaseFile, setSelectedDatabaseFile] = useState(null);
  const [includeDatabase, setIncludeDatabase] = useState(false);
  const [currentPath, setCurrentPath] = useState('');
  const [linkHistory, setLinkHistory] = useState([]);

  useEffect(() => {
    // Load GitHub link history from local storage when component mounts
    const storedLinks = JSON.parse(localStorage.getItem('githubLinkHistory')) || [];
    setLinkHistory(storedLinks);
  }, []);

  const handleFileChange = (e) => {
    const fileArray = Array.from(e.target.files);
    setFiles(fileArray);
    if (fileArray.length === 1) {
      setSelectedMainFile(fileArray[0]);
    } else {
      setSelectedMainFile(null);
    }
    setSelectedDatabaseFile(null);
    onFileUpload(fileArray);
  };

  const handleLinkChange = (e) => {
    setGithubLink(e.target.value);
    onGithubLinkChange(e.target.value);
  };

  const handleLinkSelect = (link) => {
    setGithubLink(link);
    onGithubLinkChange(link);
  };

  const addLinkToHistory = (link) => {
    if (!linkHistory.includes(link)) {
      const updatedLinks = [...linkHistory, link];
      setLinkHistory(updatedLinks);
      localStorage.setItem('githubLinkHistory', JSON.stringify(updatedLinks));
    }
  };

  const fetchRepoStructure = async () => {
    if (!githubLink) return;

    const match = githubLink.match(/github\.com\/([^\/]+)\/([^\/]+)/);
    if (!match) {
      toast.info('Invalid GitHub URL');
      return;
    }

    const [_, owner, repo] = match;
    try {
      const response = await axios.get(
        `https://api.github.com/repos/${owner}/${repo}/contents/${currentPath}`
      );

      const fetchedFiles = await Promise.all(response.data
        .filter(item => item.type === 'file')
        .map(async item => {
          const fileContentResponse = await axios.get(item.download_url, {
            responseType: 'blob',
          });
          return new File([fileContentResponse.data], item.name, { type: fileContentResponse.data.type });
        })
      );

      setRepoStructure(response.data);
      setFiles(fetchedFiles);
      onFileUpload(fetchedFiles);
      addLinkToHistory(githubLink); // Add link to history after fetching repo
      console.log('repoStructure:', fetchedFiles);
    } catch (error) {
      console.error('Error fetching repository structure:', error);
      alert('Failed to fetch repository structure');
    }
  };

  const handleFolderClick = (path) => {
    setCurrentPath(path);
    fetchRepoStructure();
  };

  const handleFileClick = (file) => {
    if (includeDatabase) {
      if (!selectedDatabaseFile) {
        setSelectedDatabaseFile(file);
      } else {
        setSelectedMainFile(file);
      }
    } else {
      setSelectedMainFile(file);
    }
  
    if (file.isGitHubFile) {
      axios.get(file.download_url, { responseType: 'blob' })
        .then(response => {
          const reader = new FileReader();
          reader.onload = () => {
            onFileUpload([file], reader.result); 
            MainFile(file.name);
          };
          reader.readAsText(response.data);
        })
        .catch(error => {
          console.error('Error fetching GitHub file content:', error);
          toast.error('Failed to load file content from GitHub.');
        });
    } else {
      const reader = new FileReader();
      reader.onload = () => {
        onFileUpload([file], reader.result); 
        MainFile(file.name);
      };
      reader.readAsText(file);
    }
  };

  const handleSubmit = async () => {
    if (includeDatabase && (!selectedDatabaseFile || !selectedMainFile)) {
      toast.info('Please select both a database file and a main file.');
      return;
    }

    if (!selectedMainFile) {
      toast.info("Please select a main file.");
      return;
    }

    const formData = new FormData();

    if (files.length > 0) {
      files.forEach(file => {
        formData.append('files', file);
      });
    }

    MainFile(selectedMainFile.name || selectedMainFile.path); 

    if (selectedMainFile) {
      formData.append('main_file_name', selectedMainFile.name || selectedMainFile.path);
    }

    if (includeDatabase && selectedDatabaseFile) {
      formData.append('database_file_name', selectedDatabaseFile.name || selectedDatabaseFile.path);
    }

    if (githubLink) {
      formData.append('github_url', githubLink);
    }

    try {
      if (selectedMainFile instanceof Blob) {
        const mainFileContent = await readFileContent(selectedMainFile);
        onFileUpload(files, mainFileContent);
      } else {
        console.log('Selected main file is from GitHub:', selectedMainFile);
      }

      const response = await axios.post('http://localhost:8000/uploads/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.status === 200) {
        console.log("Files uploaded successfully");
      } else {
        console.error("Error uploading files");
      }
    } catch (error) {
      console.error("Error uploading files:", error);
    }

    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-800 bg-opacity-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-[420px] relative">
        <FaTimes
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-600 cursor-pointer"
          size={20}
        />
        <h2 className="text-xl font-semibold mb-4">Upload Files or Paste GitHub Link</h2>
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          className="mb-4 w-full p-2 border border-gray-300 rounded-md"
        />
        <input
          type="text"
          placeholder="Paste GitHub link here"
          value={githubLink}
          onChange={handleLinkChange}
          className="mb-4 w-full p-2 border border-gray-300 rounded-md"
          list="githubLinkHistory"
        />
        <datalist id="githubLinkHistory">
          {linkHistory.map((link, index) => (
            <option key={index} value={link} onClick={() => handleLinkSelect(link)} />
          ))}
        </datalist>
        <button
          onClick={fetchRepoStructure}
          className="mb-4 w-full p-2 bg-blue-600 text-white text-sm font-medium rounded-md shadow-sm"
        >
          Load Repository
        </button>
        {files.length > 0 && !repoStructure.length && (
          <>
            <p className="text-sm text-gray-600 mb-2">
              Please select the main file that needs to run first from the files listed below:
            </p>
            <div className="max-h-[80px] overflow-y-auto mb-4">
              <ul>
                {files.map((file, index) => (
                  <li
                    key={index}
                    onClick={() => handleFileClick(file)}
                    className={`p-2 border rounded-md cursor-pointer ${
                      selectedMainFile === file ? 'bg-blue-100' : 'bg-gray-50'
                    }`}
                  >
                    {file.name}
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}

        {repoStructure.length > 0 && (
          <>
            <p className="text-sm text-gray-600 mb-2">
              Navigate through the folders and select the main file:
            </p>
            <div className="max-h-[80px] overflow-y-auto mb-4">
              <ul>
                {repoStructure.map((item, index) => (
                  <li
                    key={index}
                    onClick={() =>
                      item.type === 'dir'
                        ? handleFolderClick(item.path)
                        : handleFileClick(item)
                    }
                    className={`p-2 border rounded-md cursor-pointer ${
                      selectedMainFile && (selectedMainFile.name === item.name || selectedMainFile.path === item.path) 
                        ? 'bg-blue-100' 
                        : 'bg-gray-50'
                    }`}
                    
                  >
                    {item.type === 'dir' ? `📁 ${item.name}` : `📄 ${item.name}`}
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}

        {selectedMainFile && (
          <>
            <div className="mb-4">
              <input
                type="checkbox"
                id="includeDatabase"
                checked={includeDatabase}
                onChange={() => {
                  setIncludeDatabase(!includeDatabase);
                  if (!includeDatabase) {
                    setSelectedDatabaseFile(null);
                  }
                }}
              />
              <label htmlFor="includeDatabase" className="ml-2 text-sm text-gray-600">
                Include Database File
              </label>
            </div>
            {includeDatabase && (
              <>
                <p className="text-sm text-gray-600 mb-2">
                  Please select the database file from the files listed below:
                </p>
                <div className="max-h-[80px] overflow-y-auto mb-4">
                  <ul>
                    {files.length > 0 && !repoStructure.length && files
                      .filter(file => 
                        file !== selectedMainFile && 
                        (file.name.endsWith('.sql') || file.name.endsWith('.db') || file.name.endsWith('.mdb'))
                      ) 
                      .map((file, index) => (
                        <li
                          key={index}
                          onClick={() => handleFileClick(file)}
                          className={`p-2 border rounded-md cursor-pointer ${
                            selectedDatabaseFile === file ? 'bg-blue-100' : 'bg-gray-50'
                          }`}
                        >
                          {file.name}
                        </li>
                      ))}
                    {repoStructure.length > 0 && repoStructure
                      .filter(item => 
                        item !== selectedMainFile && 
                        (item.name.endsWith('.sql') || item.name.endsWith('.db') || item.name.endsWith('.mdb'))
                      ) 
                      .map((item, index) => (
                        <li
                          key={index}
                          onClick={() => handleFileClick(item)}
                          className={`p-2 border rounded-md cursor-pointer ${
                            selectedDatabaseFile === item.path ? 'bg-blue-100' : 'bg-gray-50'
                          }`}
                        >
                          {item.name}
                        </li>
                      ))}
                  </ul>
                </div>
              </>
            )}
          </>
        )}

        <button
          onClick={handleSubmit}
          className="w-full p-2.5 bg-green-600 text-white text-sm font-medium rounded-md shadow-sm"
        >
          Submit
        </button>
      </div>
    </div>
  );
};

export default FileUploadPopup;
