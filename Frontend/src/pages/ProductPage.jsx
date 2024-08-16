import { useState } from 'react';
import { languages } from '../data/languages.js';
import CustomDropdown from '../Components/CustomDropdown.jsx';
import SourcecodeInput from '../Components/SourcecodeInput.jsx';
import { Convertedcode } from '../Components/Convertedcode.jsx';
import SourcecodeOutput from '../Components/SourcecodeOutput.jsx';
import ConvertedcodeOutput from '../Components/ConvertedcodeOutput.jsx';
import { Navbar } from '../Layout/Navbar.jsx';
import ChangeCircleIcon from '@mui/icons-material/ChangeCircle';
import { toast } from 'react-toastify';
import axios from 'axios';

const ProductPage = () => {
  const defaultLanguage = languages[0]; // Set the first language as the default
  const [SourceLanguage, setSourceLanguage] = useState(defaultLanguage);
  const [TargetLanguage, setTargetLanguage] = useState(defaultLanguage);
  const [isConvertDisabled, setIsConvertDisabled] = useState(true);
  const [showSourcecodeOutput, setShowSourcecodeOutput] = useState(false);
  const [showConvertedcodeOutput, setShowConvertedcodeOutput] = useState(false);
  const [output, setOutput] = useState(''); // State to hold the output from the backend
  const [convertedCode, setConvertedCode] = useState(''); // State to hold the converted code

  const getRightDropdownLanguages = (leftLang) => {
    if (leftLang.value === 'sql') {
      return languages.filter((lang) => lang.value === 'pyspark');
    } else if (leftLang.value === 'pyspark') {
      return languages.filter((lang) => lang.value === 'sql');
    } else {
      return languages.filter(
        (lang) =>
          lang.value !== leftLang.value &&
          lang.value !== 'sql' &&
          lang.value !== 'pyspark'
      );
    }
  };

  const handleSourceLanguageChange = (language) => {
    console.log("Selected Source Language:", language);
    setSourceLanguage(language);
  };

  const handleTargetLanguageChange = (language) => {
    console.log("Selected Target Language:", language);
    setTargetLanguage(language);
  };

  const handleOutputChange = (content) => {
    setIsConvertDisabled(content.length === 0);
  };

  const handleRunSourcecodeInput = (output) => {
    setOutput(output); // Capture the output from the SourcecodeInput
    setShowSourcecodeOutput(true);
    setIsConvertDisabled(false); // Enable the Convert button after code execution
  };

  const handleRunConvertedcode = () => {
    setShowConvertedcodeOutput(true);
  };

  const handleConvertClick = async () => {
    if (!SourceLanguage.value || !TargetLanguage.value) {
      toast.error('Please select both source and target languages.');
      return;
    }

    console.log("Source Language:", SourceLanguage.value);
    console.log("Target Language:", TargetLanguage.value);
    

    try {
      const response = await axios.post('http://127.0.0.1:8000/conversion/', {
        source_language: SourceLanguage.value,
        target_language: TargetLanguage.value,
      });

      if (response.status === 200 && response.data.status === 'success') {
        toast.success('Code converted successfully!');
        setConvertedCode(response.data.converted_code); // Assuming 'converted_code' is the key in response
        setShowConvertedcodeOutput(true);
      } else {
        toast.error('Error converting code.');
      }
    } catch (error) {
      console.error('Error converting code:', error);
      if (error.response) {
        console.error('Backend responded with:', error.response.data);
        toast.error('An error occurred on the server.');
      } else if (error.request) {
        console.error('No response received:', error.request);
        toast.error('No response from the server.');
      } else {
        console.error('Error setting up the request:', error.message);
        toast.error('Error in setting up the request.');
      }
    }
  };

  return (
    <>
      <Navbar />
      <div className="container mx-auto px-24 py-4">
        <div className="flex flex-col items-center justify-center h-8 py-4 mb-16 my-8 w-full">
          <h1 className="text-3xl shadow-2xl drop-shadow-xl">
            Start Converting Your Legacy code
          </h1>
        </div>
        {/* language */}
        <div className="flex justify-between mb-4">
          <div className="w-1/2 pr-2">
            <label
              htmlFor="left-lang"
              className="block mb-2 text-sm font-medium text-gray-700"
            >
              Source Language
            </label>
            <CustomDropdown
                selectedLanguage={SourceLanguage}
                setSelectedLanguage={handleSourceLanguageChange}
                id="left-lang"
                availableLanguages={languages}
            />
          </div>

          <div className="w-1/2 pl-2">
            <label
              htmlFor="right-lang"
              className="block mb-2 text-sm font-medium text-gray-700"
            >
              Target Language
            </label>
            <CustomDropdown
                selectedLanguage={TargetLanguage}
                setSelectedLanguage={handleTargetLanguageChange}
                id="right-lang"
                availableLanguages={getRightDropdownLanguages(SourceLanguage)}
            />
          </div>
        </div>

        <div className="flex justify-between mb-4">
          <SourcecodeInput SourceLanguage={SourceLanguage} TargetLanguage={TargetLanguage} onRunComplete={handleRunSourcecodeInput} />
          <Convertedcode code={convertedCode} onRun={handleRunConvertedcode} />
        </div>

        <div className="mt-8 flex justify-center">
          <button
            type="button"
            className={`p-3 w-1/3 justify-center gap-2 items-center flex ${
              isConvertDisabled ? 'bg-[#b7a8f3] cursor-not-allowed' : 'bg-[#a289ef]'
            } text-white text-lg font-medium rounded-md shadow-sm`}
            onClick={handleConvertClick}
            disabled={isConvertDisabled}
          >
            <ChangeCircleIcon />
            Convert
          </button>
        </div>

        <div className="flex justify-between mt-8">
          {showSourcecodeOutput && <SourcecodeOutput content={output} onOutputChange={handleOutputChange} />}
          {showConvertedcodeOutput && <ConvertedcodeOutput />}
        </div>
      </div>
    </>
  );
};

export default ProductPage;
