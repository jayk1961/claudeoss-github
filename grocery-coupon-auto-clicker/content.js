// content.js - Core automation logic for Grocery Coupon Auto-Clicker
// Version 1.2.0 - Production Ready

(function() {
    'use strict';

    let isRunning = false;
    let clickCount = 0;
    let settings = {
        delayMin: 500,
        delayMax: 1500,
        autoScroll: true,
        maxClicks: 100
    };

    // Load settings
    chrome.storage.sync.get(settings, (items) => {
        settings = items;
    });

    // Listen for messages from popup
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.action === 'start') {
            if (!isRunning) {
                isRunning = true;
                clickCount = 0;
                startClicking();
                sendResponse({ status: 'started' });
            } else {
                sendResponse({ status: 'already_running' });
            }
        } else if (request.action === 'stop') {
            isRunning = false;
            sendResponse({ status: 'stopped', count: clickCount });
        } else if (request.action === 'getStatus') {
            sendResponse({ isRunning: isRunning, count: clickCount });
        }
        return true;
    });

    // Helper: Random delay to simulate human behavior
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    const getRandomDelay = () => Math.floor(Math.random() * (settings.delayMax - settings.delayMin + 1)) + settings.delayMin;

    // Selectors for common grocery sites
    const buttonSelectors = [
        'button:contains("Clip Coupon")',
        'button:contains("Send to Card")',
        'button:contains("Activate")',
        'button:contains("Clip")',
        '[aria-label*="Clip"]',
        '[aria-label*="Send to Card"]',
        '.clip-coupon-button',
        '.kds-Button:contains("Clip")'
    ].join(', ');

    // Custom pseudo-selector for text content (since standard CSS doesn't support :contains)
    function findButtons() {
        const buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));
        const keywords = ['clip coupon', 'send to card', 'activate', 'clip'];
        
        return buttons.filter(btn => {
            // Skip already clicked or hidden buttons
            if (btn.disabled || btn.offsetParent === null || btn.classList.contains('clicked')) {
                return false;
            }
            
            const text = (btn.innerText || btn.textContent || btn.getAttribute('aria-label') || '').toLowerCase();
            return keywords.some(keyword => text.includes(keyword)) && !text.includes('unclip');
        });
    }

    async function startClicking() {
        console.log('Grocery Coupon Auto-Clicker: Started');
        
        while (isRunning && clickCount < settings.maxClicks) {
            const buttons = findButtons();
            
            if (buttons.length === 0) {
                if (settings.autoScroll) {
                    // Try scrolling to load more
                    window.scrollBy(0, window.innerHeight);
                    await sleep(2000); // Wait for network request
                    
                    const newButtons = findButtons();
                    if (newButtons.length === 0) {
                        console.log('No more coupons found after scrolling.');
                        isRunning = false;
                        break;
                    }
                } else {
                    console.log('No more coupons found.');
                    isRunning = false;
                    break;
                }
            } else {
                for (const btn of buttons) {
                    if (!isRunning || clickCount >= settings.maxClicks) break;
                    
                    try {
                        btn.click();
                        btn.classList.add('clicked'); // Mark as clicked to avoid infinite loops
                        clickCount++;
                        console.log(`Clicked coupon ${clickCount}`);
                        
                        // Notify popup of progress
                        chrome.runtime.sendMessage({ action: 'updateCount', count: clickCount });
                        
                        await sleep(getRandomDelay());
                    } catch (e) {
                        console.error('Error clicking button:', e);
                    }
                }
            }
        }
        
        isRunning = false;
        console.log(`Grocery Coupon Auto-Clicker: Finished. Total clicked: ${clickCount}`);
        chrome.runtime.sendMessage({ action: 'finished', count: clickCount });
    }
})();