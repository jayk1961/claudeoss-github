# Grocery Coupon Auto-Clicker – CVS, Safeway, Albertsons & More

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/jayk1961/grocery-coupon-auto-clicker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust, production-ready Manifest V3 browser extension that automatically clicks "Clip Coupon", "Send to Card", and "Activate" buttons on major grocery store websites.

## Features
- **Multi-Store Support**: Works out-of-the-box on CVS, Safeway, Albertsons, Vons, Kroger, Walgreens, and more.
- **Human-like Delays**: Randomizes click intervals to mimic human behavior and prevent rate-limiting.
- **Infinite Scroll**: Automatically scrolls down to load and clip more coupons.
- **Customizable Settings**: Adjust minimum/maximum delays, maximum clicks per session, and toggle auto-scroll.
- **Cross-Browser Compatible**: Built on Manifest V3, ready for Chrome Web Store, Edge Add-ons, and Firefox AMO.

## Installation (End Users)
1. Download the latest release from the [Releases page](https://github.com/jayk1961/grocery-coupon-auto-clicker/releases).
2. Unzip the downloaded file.
3. Open your browser's extension management page:
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`
   - Firefox: `about:debugging#/runtime/this-firefox`
4. Enable "Developer mode" (top right corner in Chrome/Edge).
5. Click "Load unpacked" and select the unzipped directory.

## Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/jayk1961/grocery-coupon-auto-clicker.git
   ```
2. Make your changes to `content.js`, `popup.js`, or `options.js`.
3. Reload the extension in your browser to test changes.

## Privacy Policy
This extension runs entirely locally in your browser. It does not collect, store, or transmit any personal data, browsing history, or account information.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Maintainer
Maintained by [jayk1961](https://github.com/jayk1961).
This project is actively maintained and serves as a demonstration of production-quality open-source development.