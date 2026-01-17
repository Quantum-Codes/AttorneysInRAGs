/**
 * Global variable for use within this script.
 * Note: This will reset if the script is reloaded (e.g., closing/opening a popup).
 */
let extractedText: string = "";

/**
 * Main execution flow
 */
async function handleDataExtraction() {
  try {
    // 1. Fetch data from the background/content script
    const res = await chrome.runtime.sendMessage({ message: "fetch_raw_text" });

    if (res?.rawText) {
      // 2. Store in local variable for immediate use in this script
      extractedText = res.rawText;
      alert(extractedText)
      // 3. Persist in Chrome Storage for use in other scripts or sessions
      await chrome.storage.local.set({
        savedText: res.rawText,
        siteName: stripURL(res.pageURL),
        docType: res.docType
      });

      // 4. Trigger subsequent logic
      runOtherCode();
    }
  } catch (error) {
    console.error("Failed to fetch or store data:", error);
  }
}

/**
 * Example of how to use the data in another function
 */
function runOtherCode() {
  if (extractedText) {
    console.log("Processing text from variable:", extractedText.substring(0, 50) + "...");
  }
}

/**
 * Utility: URL Cleanup logic
 */
function stripURL(url: string): string {
  if (!url) return "this service";

  const domainRegex = /^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)/;
  const match = url.match(domainRegex);

  return (match && match[1]) ? match[1] : "this service";
}

// Initialize the process when the script loads
handleDataExtraction();
