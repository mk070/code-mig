import { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FaTimes } from 'react-icons/fa'; // Import the close icon from react-icons

const FileUploadPopup = ({ onClose, onFileUpload, onGithubLinkChange }) => {
  const [githubLink, setGithubLink] = useState('');
  const [repoStructure, setRepoStructure] = useState([]);
  const [files, setFiles] = useState([]);
  const [selectedMainFile, setSelectedMainFile] = useState(null);
  const [selectedDatabaseFile, setSelectedDatabaseFile] = useState(null);
  const [includeDatabase, setIncludeDatabase] = useState(false);
  const [currentPath, setCurrentPath] = useState('');

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
      setRepoStructure(response.data);
      setFiles([]);
    } catch (error) {
      console.error('Error fetching repository structure:', error);
      alert('Failed to fetch repository structure');
    }
  };

  const handleFolderClick = (path) => {
    setCurrentPath(path);
    fetchRepoStructure();
  };

  const handleFileClick = (filePath) => {
    if (includeDatabase) {
      if (!selectedDatabaseFile) {
        setSelectedDatabaseFile(filePath);
      } else {
        setSelectedMainFile(filePath);
      }
    } else {
      setSelectedMainFile(filePath);
    }
  };

  const readFileContent = async (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsText(file);
    });
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

    if (selectedMainFile) {
      formData.append('main_file_name', selectedMainFile.name); // Send filename as string
    }

    if (includeDatabase && selectedDatabaseFile) {
      formData.append('database_file_name', selectedDatabaseFile.name); // Send filename as string
    }

    if (githubLink) {
      formData.append('github_link', githubLink);
    }

    try {
      const mainFileContent = await readFileContent(selectedMainFile);

      onFileUpload(files, mainFileContent);

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
        />
        <button
          onClick={fetchRepoStructure}
          className="mb-4 w-full p-2 bg-blue-600 text-white text-sm font-medium rounded-md shadow-sm"
        >
          Load Repository
        </button>
        {files.length > 0 && (
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
                        setSelectedDatabaseFile(null); // Reset database file selection when checkbox is unchecked
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
                        {files
                          .filter(file => file !== selectedMainFile) // Exclude the main file
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
                      </ul>
                    </div>
                  </>
                )}
              </>
            )}
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
                        : handleFileClick(item.path)
                    }
                    className={`p-2 border rounded-md cursor-pointer ${
                      selectedMainFile === item.path || selectedDatabaseFile === item.path ? 'bg-blue-100' : 'bg-gray-50'
                    }`}
                  >
                    {item.type === 'dir' ? `📁 ${item.name}` : `📄 ${item.name}`}
                  </li>
                ))}
              </ul>
            </div>
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
