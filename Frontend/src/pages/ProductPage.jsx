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

const ProductPage = () => {
  const defaultLanguage = languages[0]; // Set the first language as the default
  const [leftLanguage, setLeftLanguage] = useState(defaultLanguage);
  const [rightLanguage, setRightLanguage] = useState(defaultLanguage);
  const [isConvertDisabled, setIsConvertDisabled] = useState(true);
  const [showSourcecodeOutput, setShowSourcecodeOutput] = useState(false);
  const [showConvertedcodeOutput, setShowConvertedcodeOutput] = useState(false);

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

  const handleOutputChange = (content) => {
    setIsConvertDisabled(content.length === 0);
  };

  const handleConvertClick = () => {
    if (isConvertDisabled) {
      toast.info('Please run the source code to convert the code');
    }
  };

  const handleRunSourcecodeInput = () => {
    setShowSourcecodeOutput(true);
  };

  const handleRunConvertedcode = () => {
    setShowConvertedcodeOutput(true);
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
              Select Language
            </label>
            <CustomDropdown
              selectedLanguage={leftLanguage}
              setSelectedLanguage={setLeftLanguage}
              id="left-lang"
              availableLanguages={languages}
            />
          </div>

          <div className="w-1/2 pl-2">
            <label
              htmlFor="right-lang"
              className="block mb-2 text-sm font-medium text-gray-700"
            >
              Select Language
            </label>
            <CustomDropdown
              selectedLanguage={rightLanguage}
              setSelectedLanguage={setRightLanguage}
              id="right-lang"
              availableLanguages={getRightDropdownLanguages(leftLanguage)}
            />
          </div>
        </div>

        <div className="flex justify-between mb-4">
          <SourcecodeInput onRun={handleRunSourcecodeInput} />
          <Convertedcode onRun={handleRunConvertedcode} />
        </div>

        <div className="mt-8 flex justify-center">
          <button
            type="button"
            className={`p-3 w-1/3 justify-center gap-2 items-center flex ${
              isConvertDisabled ? 'bg-[#b7a8f3] cursor-not-allowed' : 'bg-[#a289ef]'
            } text-white text-lg font-medium rounded-md shadow-sm`}
            onClick={handleConvertClick}
          >
            <ChangeCircleIcon />
            Convert
          </button>
        </div>

        <div className="flex justify-between mt-8">
          {showSourcecodeOutput && <SourcecodeOutput onOutputChange={handleOutputChange} />}
          {showConvertedcodeOutput && <ConvertedcodeOutput />}
        </div>
      </div>
    </>
  );
};

export default ProductPage;
