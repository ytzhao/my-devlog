/*
  Background script — DevLog Web Highlighter
  Only handles tab screenshot capture (content script cannot call captureVisibleTab).
  Save requests are sent directly from content script via fetch to localhost:3721.
*/

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action !== 'captureFullPage') return false;

  (async () => {
    try {
      const dataUrl = await chrome.tabs.captureVisibleTab(undefined, { format: 'png', quality: 95 });
      sendResponse({ status: 'ok', dataUrl });
    } catch (err) {
      sendResponse({ status: 'error', message: err.message });
    }
  })();

  return true;
});
