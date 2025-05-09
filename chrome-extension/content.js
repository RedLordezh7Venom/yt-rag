// content.js
// Notifies background to get the current video URL
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'REQUEST_VIDEO_URL') {
    sendResponse({ url: window.location.href });
  }
});
