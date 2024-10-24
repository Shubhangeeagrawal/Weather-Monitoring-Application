# Weather-Monitoring-Application
This project implements a Weather Monitoring system that tracks and analyzes weather data. The application can pull data from external APIs or sensors and store it in a database. It uses a web interface to display weather conditions and trends.

## Table of Contents
- Features
- Requirements
- Setup Instructions
- Usage
- Design Choices
- Project Structure
- Contributing

## Features
- Collects weather data (e.g., temperature, humidity, wind speed) from external APIs or IoT sensors.
- Displays real-time weather conditions and historical trends through a web-based interface.
- Can store weather data in a database for long-term analysis.

## Requirements
- Python 3.x
- Docker or Podman (for containerized services)

## Dependencies
- Flask (for the webserver)
- SQLite/MySQL/PostgreSQL (for the database)
- Docker or Podman installed on your machine.

Install the Python dependencies using:
**bash**
pip install -r requirements.txt

Alternatively, create and activate a virtual environment:
**bash**
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## Setup Instructions
### Step 1: Clone the Repository
**bash**
git clone https://github.com/Shubhangeeagrawal/weather-monitoring.git
cd weather-monitoring

### Step 2: Build and Run the Application
You can use Docker Compose to set up the web server and database containers.
1.Run the following command to build and start the containers:
**bash**
docker-compose up --build

This will:
- Build the web server image (using Flask or another web framework).
- Start the database container (MySQL, PostgreSQL, or SQLite).
2.The application should be available at http://localhost:5000.
### Step 3: Running Manually
If you prefer not to use Docker:
1.Start the Flask server:
**bash**
python app.py

2.Configure your database connection in config.py or through environment variables to use a local database.

## Usage
1.Weather Data Collection: The application collects weather data from connected sensors or external APIs.
2.Displaying Weather Information: Data is visualized through a user-friendly web interface.
3.Historical Data: Users can view historical weather trends.

## Design Choices
1.Containerization with Docker/Podman:
  - Docker/Podman simplifies the deployment process by encapsulating the database and web server in separate containers, making it easier to manage dependencies and scale.

2.Modular Code Structure:
  - The application is divided into multiple layers:
    - Presentation Layer: A web interface built using Flask.
    - Application Layer: Handles the logic for weather data collection and analysis.
    - Data Layer: Stores weather data in the database for further analysis.

3.Database Support:
  - The use of a relational database (like SQLite, MySQL, or PostgreSQL) allows for long-term storage and querying of weather data, facilitating trend analysis and reporting.

## Project Structure
**bash**
weather-monitoring/
│
├── app.py               # Main application file
├── weather_Monitoring.py # Weather monitoring logic
├── config.py             # Configuration for database and APIs
├── Dockerfile            # Dockerfile for building the web server image
├── docker-compose.yml    # Docker Compose file for managing services
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation (this file)

## Contributing
To contribute:
1.Fork the repository.
2.Create a new feature branch (git checkout -b feature-branch).
3.Commit your changes (git commit -am 'Add feature').
4.Push to the branch (git push origin feature-branch).
5.Open a pull request.
