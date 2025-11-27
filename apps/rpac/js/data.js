// Data loader with fallback support
let CHALLENGE_DATA = [];
let dataLoadedPromise = null;

/**
 * Load challenge data from JSON file (idempotent).
 * @returns {Promise<boolean>} True if data loaded successfully
 */
async function loadChallengeData() {
  // Return cached promise if already loading/loaded
  if (!dataLoadedPromise) {
    dataLoadedPromise = (async () => {
      try {
        const response = await fetch('data/challenge-data.json');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const json = await response.json();
        CHALLENGE_DATA = json.records;
        console.log(`[DATA] Loaded ${CHALLENGE_DATA.length} records from JSON`);
        return true;
      } catch (error) {
        console.error('[DATA] Failed to load challenge-data.json:', error);
        return false;
      }
    })();
  }
  return dataLoadedPromise;
}

// Export for global access
window.CHALLENGE_DATA = CHALLENGE_DATA;
window.loadChallengeData = loadChallengeData;
