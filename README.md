# Carelytics – Health Risk Explorer

This project combines three separate machine‑learning models (blood pressure, diabetes, and daily mental health) into a unified, web‑based risk explorer.

# Home page 

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

# Mental health Analysis page 

<table>
  <tr>
    <td width="50%">
      <img width="100%" alt="image" src="https://github.com/user-attachments/assets/aa1f8e3a-9f94-4cda-abac-cfa43711ff08"/>
    </td>
    <td width="50%">
      <img width="100%" alt="image" src="https://github.com/user-attachments/assets/7a58db26-39c2-499b-8064-8c43b4611046" />
    </td>
  </tr>
</table>
<table>
  <tr>
    <td width="50%">
      <img width="100%" alt="image" src="https://github.com/user-attachments/assets/df5c8f21-a53d-4edd-9521-694aa5701adf />
    </td>
    <td width="50%">
      <img width="100%" alt="image" src="https://github.com/user-attachments/assets/f80af908-ec41-4a0e-adff-0845538c89de" />
    </td>
  </tr>
</table>


<table>
  <tr>
    <td width="50%">
      <img width="100%" alt="image" src="https://github.com/user-attachments/assets/5610552e-c957-4da9-ac3c-7a840e408647" />
    </td>
    <td width="50%">
      <img width="100%" alt="image" src="src="https://github.com/user-attachments/assets/28e5aaec-eb3b-474b-b049-a2f6e16cb6dc" />
    </td>
  </tr>
</table>


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
