import React, { useState, useEffect } from 'react';
import { FaSpinner, FaCog, FaCircleNotch, FaExchangeAlt, FaSyncAlt, FaCheckCircle } from 'react-icons/fa';

const Loader = ({ mode }) => {
  const [iconIndex, setIconIndex] = useState(0);
  const [messageIndex, setMessageIndex] = useState(0);

  const compileIcons = [
    <FaSpinner className="animate-spin text-6xl text-white" />,
    <FaCog className="animate-spin text-6xl text-white" />,
    <FaCircleNotch className="animate-spin text-6xl text-white" />,
  ];

  const convertIcons = [
    <FaExchangeAlt className="animate-spin text-6xl text-white" />,
    <FaSyncAlt className="animate-spin text-6xl text-white" />,
    <FaCog className="animate-spin text-6xl text-white" />,
  ];

  const accuracyIcons = [
    <FaCheckCircle className="animate-spin text-6xl text-white" />,
    <FaSpinner className="animate-spin text-6xl text-white" />,
    <FaSyncAlt className="animate-spin text-6xl text-white" />,
  ];

  const compileMessages = [
    "Your code is compiling, please wait...",
    "Almost there, hang tight...",
    "Finalizing the execution, just a moment...",
  ];

  const convertMessages = [
    "Converting your code, please wait...",
    "Transformation in progress, hang tight...",
    "Almost done converting, just a moment...",
  ];

  const accuracyMessages = [
    "Analyzing accuracy, please wait...",
    "Evaluating results, almost done...",
    "Finalizing accuracy report, just a moment...",
  ];

  const icons = mode === 'convert' ? convertIcons 
              : mode === 'accuracy' ? accuracyIcons 
              : compileIcons;

  const messages = mode === 'convert' ? convertMessages 
                : mode === 'accuracy' ? accuracyMessages 
                : compileMessages;

  useEffect(() => {
    const iconInterval = setInterval(() => {
      setIconIndex((prevIndex) => (prevIndex + 1) % icons.length);
    }, 3000); // Change icon every 3 seconds

    const messageInterval = setInterval(() => {
      setMessageIndex((prevIndex) => (prevIndex + 1) % messages.length);
    }, 3000); // Change message every 3 seconds

    return () => {
      clearInterval(iconInterval);
      clearInterval(messageInterval);
    };
  }, [icons.length, messages.length]);

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black bg-opacity-75">
      <div className="flex items-center justify-center mb-4">
        {icons[iconIndex]}
      </div>
      <span className="text-white text-xl">{messages[messageIndex]}</span>
    </div>
  );
};

export default Loader;
