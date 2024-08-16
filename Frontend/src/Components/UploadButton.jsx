import { useState } from 'react';
import UploadIcon from '@mui/icons-material/Upload';
import FileUploadPopup from './FileUploadPopup';

const UploadButton = ({ onFileUpload, onGithubLinkChange }) => {
  const [openPopup, setOpenPopup] = useState(false);

  const handleButtonClick = () => {
    setOpenPopup(true);
  };
  const handleClosePopup = () => {
    setOpenPopup(false);
  };

  return (
    <>
      <button
        onClick={handleButtonClick}
        className="flex items-center p-2 bg-blue-500 text-white rounded-md"
      >
        <UploadIcon className="mr-2" />
        Upload
      </button>
      {openPopup && (
        <FileUploadPopup
          onClose={handleClosePopup}
          onFileUpload={onFileUpload}
          onGithubLinkChange={onGithubLinkChange}
        />
      )}
    </>
  );
};

export default UploadButton;
