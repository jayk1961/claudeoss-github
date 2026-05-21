document.addEventListener('DOMContentLoaded', () => {
    const delayMinInput = document.getElementById('delayMin');
    const delayMaxInput = document.getElementById('delayMax');
    const maxClicksInput = document.getElementById('maxClicks');
    const autoScrollInput = document.getElementById('autoScroll');
    const saveBtn = document.getElementById('saveBtn');
    const statusDiv = document.getElementById('status');

    // Default settings
    const defaultSettings = {
        delayMin: 500,
        delayMax: 1500,
        maxClicks: 100,
        autoScroll: true
    };

    // Load current settings
    chrome.storage.sync.get(defaultSettings, (items) => {
        delayMinInput.value = items.delayMin;
        delayMaxInput.value = items.delayMax;
        maxClicksInput.value = items.maxClicks;
        autoScrollInput.checked = items.autoScroll;
    });

    // Save settings
    saveBtn.addEventListener('click', () => {
        let min = parseInt(delayMinInput.value, 10);
        let max = parseInt(delayMaxInput.value, 10);
        
        // Validation
        if (min > max) {
            alert("Minimum delay cannot be greater than maximum delay.");
            return;
        }

        const settings = {
            delayMin: min,
            delayMax: max,
            maxClicks: parseInt(maxClicksInput.value, 10),
            autoScroll: autoScrollInput.checked
        };

        chrome.storage.sync.set(settings, () => {
            statusDiv.style.display = 'block';
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        });
    });
});