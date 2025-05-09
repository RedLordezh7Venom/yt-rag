// background.js (service worker)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_VIDEO_URL') {
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      const url = tabs[0]?.url || '';
      sendResponse({ url });
    });
    return true; // async
  }
});
