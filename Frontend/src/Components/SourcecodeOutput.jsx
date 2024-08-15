import React, { useEffect } from 'react';

const SourcecodeOutput = ({ onOutputChange }) => {
  const [content, setContent] = React.useState('');

  useEffect(() => {
    onOutputChange(content);
  }, [content, onOutputChange]);

  const handleChange = (e) => {
    setContent(e.target.value);
  };

  return (
    <div className="w-1/2 pr-2">
      <label
        htmlFor="left-output"
        className="block mb-2 text-sm font-medium text-gray-300"
      >
        Output
      </label>
      <textarea
        id="left-output"
        rows="10"
        className="w-full p-2.5 border border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-black text-green-400 font-mono"
        placeholder="Output will appear here..."
        value={content}
        onChange={handleChange}
        readOnly
      ></textarea>
    </div>
  );
};

export default SourcecodeOutput;
