import React from 'react';

const ConvertedcodeOutput = () => {
  return (
    <div className="w-1/2 pl-2">
      <label
        htmlFor="right-output"
        className="block mb-2 text-sm font-medium text-gray-300"
      >
        Output
      </label>
      <textarea
        id="right-output"
        rows="10"
        className="w-full p-2.5 border border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-black text-green-400 font-mono"
        placeholder="Output will appear here..."
        readOnly
      ></textarea>
    </div>
  );
};

export default ConvertedcodeOutput;
