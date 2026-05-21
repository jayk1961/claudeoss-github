document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const optionsBtn = document.getElementById('optionsBtn');
    const statusText = document.getElementById('statusText');
    const clickCount = document.getElementById('clickCount');

    // Check current status
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        if (!tabs[0]) return;
        
        chrome.tabs.sendMessage(tabs[0].id, {action: 'getStatus'}, (response) => {
            if (chrome.runtime.lastError) {
                // Content script not injected or not a supported page
                statusText.textContent = 'Navigate to a coupon page';
                startBtn.disabled = true;
                startBtn.style.opacity = '0.5';
                return;
            }
            
            if (response) {
                updateUI(response.isRunning, response.count);
            }
        });
    });

    // Listen for updates from content script
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.action === 'updateCount') {
            clickCount.textContent = request.count;
        } else if (request.action === 'finished') {
            updateUI(false, request.count);
            statusText.textContent = 'Finished!';
        }
    });

    startBtn.addEventListener('click', () => {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, {action: 'start'}, (response) => {
                if (response && response.status === 'started') {
                    updateUI(true, 0);
                }
            });
        });
    });

    stopBtn.addEventListener('click', () => {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, {action: 'stop'}, (response) => {
                if (response && response.status === 'stopped') {
                    updateUI(false, response.count);
                    statusText.textContent = 'Stopped';
                }
            });
        });
    });

    optionsBtn.addEventListener('click', () => {
        if (chrome.runtime.openOptionsPage) {
            chrome.runtime.openOptionsPage();
        } else {
            window.open(chrome.runtime.getURL('options.html'));
        }
    });

    function updateUI(isRunning, count) {
        if (isRunning) {
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            statusText.textContent = 'Clipping...';
        } else {
            startBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            if (statusText.textContent === 'Clipping...') {
                statusText.textContent = 'Ready to clip';
            }
        }
        if (count !== undefined) {
            clickCount.textContent = count;
        }
    }
});