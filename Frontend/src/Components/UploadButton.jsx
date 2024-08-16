import { useState } from 'react';
import UploadIcon from '@mui/icons-material/Upload';
import FileUploadPopup from './FileUploadPopup';

const UploadButton = ({ onFileUpload, onGithubLinkChange }) => {
  const [openPopup, setOpenPopup] = useState(false);

  const handleButtonClick = () => {
    setOpenPopup(true);
  };

  return (
    <>
      <button
        onClick={handleButtonClick}
        className="ml-2 w-full p-2.5 bg-blue-600 text-white text-sm font-medium rounded-md shadow-sm flex items-center justify-center"
      >
        <UploadIcon className="mr-2" />
        Upload Files or Link
      </button>
      {openPopup && (
        <FileUploadPopup
          onClose={() => setOpenPopup(false)}
          onFileUpload={onFileUpload}
          onGithubLinkChange={onGithubLinkChange}
        />
      )}
    </>
  );
};

export default UploadButton;
