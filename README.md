# Carelytics – Health Risk Explorer

This project combines three separate machine‑learning models (blood pressure, diabetes, and daily mental health) into a unified, web‑based risk explorer.
Login Page 

<table>
  <tr>
    <td width="50%">
      <img width="100%" alt="image" src="https://github.com/user-attachments/assets/fc7cfe5d-8686-4c6d-8ca5-dd9ecabe1057" />
    </td>
    <td width="50%">
      <img width="100%" alt="image" src="https://github.com/user-attachments/assets/59461358-c5a7-4273-ad74-97a43d9d83f0" />
    </td>
  </tr>
</table>

<img width="1340" height="835" alt="image" src="https://github.com/user-attachments/assets/70c461a0-b8bc-4803-a084-25616aa29613" />

## How to run the project

### 1. Set up the Python environment (first time only)

From the project root:

```bash


# (Optional, but recommended) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install flask joblib pandas scikit-learn
```

### 2. Start the backend + frontend

Every time you want to run the app:

```bash

source .venv/bin/activate

# Start the Flask API server
python api_server.py
# or explicitly via the venv:
# .venv/bin/python api_server.py
```

By default the server runs on:

- http://localhost:5001/

Open that URL in your browser. You’ll see the home page with buttons for:

- Mental Health Analysis
- Diabetes Analysis
- Blood Pressure Analysis
- Overall Risk Analysis

Click a card to open the corresponding analysis page. Each page:

- Lets you enter inputs.
- Calls the Flask API endpoint.
- Shows the estimated probability and risk level (LOW / MEDIUM / HIGH).
- Displays a Feature Impact or Component Breakdown view.

### 3. Stopping the server

In the terminal where `api_server.py` is running, press `Ctrl + C`.

If you used a virtual environment and want to leave it:

```bash
deactivate
```

(Or `conda deactivate` if you are in a conda environment.)

---
