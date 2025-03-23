# Minecraft Server Scanner

A Django-based web application for monitoring and analyzing Minecraft servers. Track server status, player counts, and generate analytics in real-time.

## Features

- Real-time Minecraft server monitoring
- Player tracking and session analytics
- Server status tracking (online/offline)
- Historical data analysis
- Background task scheduling for continuous monitoring

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcscanner.git
cd mcscanner
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix or macOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

## Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:8000/
```

## Features in Detail

### Server Monitoring
- Track multiple Minecraft servers simultaneously
- Real-time player count monitoring
- Server version and MOTD tracking
- Online/offline status monitoring

### Analytics Dashboard
- Historical player count data
- Peak player counts
- Average player counts
- Player session tracking
- Server performance metrics

### Background Tasks
- Automated server status checks
- Player session tracking
- Data collection and storage

## Acknowledgments

- Django web framework
- Bootstrap for the UI
- MCServerStatus API for Minecraft server data 