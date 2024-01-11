These instructions will help you get a copy of the project up and running on your local machine or on a Server (Linux / Debian)

### Prerequisites

- Python (version 3.11.4)
- everything in the requirements.txt

### Setting Up the Python Environment

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/GuardianAITech/backend-python.git
   ```

2. Navigate to the project directory:

   ```bash
   cd your-repository
   ```

3. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:

   - On Windows:

     ```bash
     .\venv\Scripts\activate
     ```

   - On Unix or MacOS:

     ```bash
     source venv/bin/activate
     ```

### Installing Requirements

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Starting the Flask Server

To start the Flask server, run the following command:

```bash
python guardianapi.py
```

### SETUP your Flask Server on a Server

1. Install gunicorn

```bash
pip install gunicorn
```

2. Create a systemd service file for your Flask application

```bash
touch /etc/systemd/system/guardianapi.service
```

3. Open the file in a text editor and add the following content:

```bash
[Unit]
Description=GuardianAPI Flask App
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/backend-python
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 guardianapi:app

[Install]
WantedBy=multi-user.target

```

Replace your_username with your actual username and /path/to/backend-python

4. Enable and start the systemd service:

```bash
sudo systemctl enable guardianapi.service
sudo systemctl start guardianapi.service
```

This will start your Flask application as a background service, and it will automatically restart if it crashes.
Now, your Flask application should be accessible on the server's IP address or domain name.
