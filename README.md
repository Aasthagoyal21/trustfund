# TrustFund - Blockchain-Based Donation Tracker

A web application that records donations and NGO expenses in a SHA-256 hash-chained ledger, making any tampering easy to detect.

## Features
- Donor registration and login, plus admin login
- Donations with a unique receipt hash
- Admin-only expense recording
- Public ledger and dashboard with chart
- Chain verification (Valid / Tampered, with the exact block number)

## Tech Stack
Python, Flask, SQLite, hashlib (SHA-256), HTML, CSS, Chart.js

## How to Run
1. Install Flask: `pip install flask`
2. Start the app: `python app.py`
3. Open `http://127.0.0.1:5000` in your browser

## Demo Admin Login
- Email: admin@trustfund.com
- Password: admin123

## Tamper Demo
1. Run `python tamper.py 100` (changes the amount of block 2)
2. Open the Verify page: it shows TAMPERED at block 2
3. Restore the original amount with `python tamper.py <original amount>`

## Limitations
This is a single-server hash-chained ledger, not a decentralised network. It detects tampering but does not prevent deletion of the whole database.

## Future Scope
Anchoring the latest hash on Ethereum, payment gateway integration, email receipts, smart contracts and multi-NGO support.