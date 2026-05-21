// background.js - Service Worker for Grocery Coupon Auto-Clicker

chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('Grocery Coupon Auto-Clicker installed successfully.');
        // Initialize default settings
        chrome.storage.sync.set({
            delayMin: 500,
            delayMax: 1500,
            autoScroll: true,
            maxClicks: 100
        });
    } else if (details.reason === 'update') {
        console.log(`Grocery Coupon Auto-Clicker updated to version ${chrome.runtime.getManifest().version}.`);
    }
});

// Optional: Handle icon clicks or other background tasks
chrome.action.onClicked.addListener((tab) => {
    // The popup handles the UI, but we could inject scripts here if needed
});