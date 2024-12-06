import React, { useCallback, useState } from 'react';
import { Document, Page } from 'react-pdf';
import 'react-pdf/dist/cjs/Page/AnnotationLayer.css';
import 'react-pdf/dist/cjs/Page/TextLayer.css';
import samplePDF from '/test.pdf';

function highlightPattern(text, pattern) {
  return text.replace(pattern, (value) => `<mark>${value}</mark>`);
}

export default function App() {
  const [searchText, setSearchText] = useState('art');

  const textRenderer = useCallback(
    (textItem) => highlightPattern(textItem.str, searchText),
    [searchText]
  );

  function onChange(event) {
    setSearchText(event.target.value);
  }

  return (
    <>
      <Document file={samplePDF}>
        <Page
          pageNumber={10}
          customTextRenderer={textRenderer}
        />
      </Document>
      <div>
        <label htmlFor="search">Search:</label>
        <input type="search" id="search" value={searchText} onChange={onChange} />
      </div>
    </>
  );
}