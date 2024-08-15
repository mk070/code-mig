import React from 'react'
import { useState } from 'react';
import { languages } from '../data/languages.js';


const CustomDropdown = ({ selectedLanguage, setSelectedLanguage, id, availableLanguages }) => {
    const [isOpen, setIsOpen] = useState(false);
  
    const handleSelect = (lang) => {
      setSelectedLanguage(lang);
      setIsOpen(false);
    };
  
    return (
      <div className="relative">
        <button
          type="button"
          id={id}
          className="w-full p-2.5 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          onClick={() => setIsOpen(!isOpen)}
        >
          <div className="flex items-center">
            {selectedLanguage && (
              <>
                <img src={selectedLanguage?.image} alt={selectedLanguage?.label} className="w-[30px] h-[30px] mr-2" />
                <span>{selectedLanguage.label}</span>
              </>
            )}
          </div>
        </button>
        {isOpen && (
          <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
            {availableLanguages.map((lang) => (
              <li
                key={lang.value}
                className="flex items-center p-2 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSelect(lang)}
              >
                <img src={lang.image} alt={lang.label} className="w-6 h-6 mr-2" />
                <span>{lang.label}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  };
  

export default CustomDropdown