import  { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

const FileUploadPopup = ({ onClose, onFileUpload, onGithubLinkChange }) => {
  const [githubLink, setGithubLink] = useState('');
  const [repoStructure, setRepoStructure] = useState([]);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [currentPath, setCurrentPath] = useState('');

  const handleFileChange = (e) => {
    const fileArray = Array.from(e.target.files);
    setFiles(fileArray);
    setSelectedFile(null); 
    setRepoStructure([]); 
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
    setSelectedFile(filePath);
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      toast.info("Please select a main file.");
      return;
    }

    const formData = new FormData();
    
  
    if (files.length > 0) {
      files.forEach(file => {
        formData.append('files', file);
      });
    }
    

    formData.append('main_file', selectedFile);
    

    if (githubLink) {
      formData.append('github_link', githubLink);
    }

    try {
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
      <div className="bg-white p-6 rounded-lg shadow-lg w-96">
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
            <div className="max-h-48 overflow-y-auto mb-4">
              <ul>
                {files.map((file, index) => (
                  <li
                    key={index}
                    onClick={() => handleFileClick(file.name)}
                    className={`p-2 border rounded-md cursor-pointer ${
                      selectedFile === file.name ? 'bg-blue-100' : 'bg-gray-50'
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
            <div className="max-h-48 overflow-y-auto mb-4">
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
                      selectedFile === item.path ? 'bg-blue-100' : 'bg-gray-50'
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
        <button
          onClick={onClose}
          className="mt-2 w-full p-2.5 bg-gray-300 text-gray-700 text-sm font-medium rounded-md shadow-sm"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

export default FileUploadPopup;
