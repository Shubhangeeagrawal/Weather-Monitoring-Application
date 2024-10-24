#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import json
import time
from datetime import datetime
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from collections import Counter

class WeatherMonitoringSystem:
    def __init__(self):
        self.api_key = "369cbb31352050b083aa84eb5f891ead"  # Replace with your OpenWeatherMap API key
        self.cities = {
            "Delhi": {"lat": 28.6139, "lon": 77.2090},
            "Mumbai": {"lat": 19.0760, "lon": 72.8777},
            "Chennai": {"lat": 13.0827, "lon": 80.2707},
            "Bangalore": {"lat": 12.9716, "lon": 77.5946},
            "Kolkata": {"lat": 22.5726, "lon": 88.3639},
            "Hyderabad": {"lat": 17.3850, "lon": 78.4867}
        }
        self.db_init()
        self.temperature_threshold = 35  # in Celsius
        self.consecutive_threshold_breaches = 0

    def db_init(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('weather_data.db')
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                temperature REAL,
                feels_like REAL,
                weather_condition TEXT,
                timestamp INTEGER
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                date TEXT,
                avg_temp REAL,
                max_temp REAL,
                min_temp REAL,
                dominant_condition TEXT
            )
        ''')
        
        self.conn.commit()

    def kelvin_to_celsius(self, kelvin):
        """Convert temperature from Kelvin to Celsius"""
        return kelvin - 273.15

    def get_weather_data(self, city, lat, lon):
        """Retrieve weather data from OpenWeatherMap API"""
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                weather_data = {
                    'city': city,
                    'temperature': self.kelvin_to_celsius(data['main']['temp']),
                    'feels_like': self.kelvin_to_celsius(data['main']['feels_like']),
                    'weather_condition': data['weather'][0]['main'],
                    'timestamp': data['dt']
                }
                return weather_data
            else:
                print(f"Error retrieving data for {city}: {data['message']}")
                return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def store_weather_data(self, weather_data):
        """Store weather data in database"""
        if weather_data:
            self.cursor.execute('''
                INSERT INTO weather_data (city, temperature, feels_like, weather_condition, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                weather_data['city'],
                weather_data['temperature'],
                weather_data['feels_like'],
                weather_data['weather_condition'],
                weather_data['timestamp']
            ))
            self.conn.commit()

    def calculate_daily_summary(self, city):
        """Calculate daily weather summary"""
        today = datetime.now().date().isoformat()
        
        self.cursor.execute('''
            SELECT AVG(temperature) as avg_temp,
                   MAX(temperature) as max_temp,
                   MIN(temperature) as min_temp,
                   GROUP_CONCAT(weather_condition) as conditions
            FROM weather_data
            WHERE city = ? AND date(datetime(timestamp, 'unixepoch')) = ?
        ''', (city, today))
        
        result = self.cursor.fetchone()
        
        if result[0] is not None:
            conditions = result[3].split(',')
            dominant_condition = Counter(conditions).most_common(1)[0][0]
            
            self.cursor.execute('''
                INSERT INTO daily_summaries (city, date, avg_temp, max_temp, min_temp, dominant_condition)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (city, today, result[0], result[1], result[2], dominant_condition))
            
            self.conn.commit()

    def check_temperature_threshold(self, weather_data):
        """Check if temperature exceeds threshold"""
        if weather_data['temperature'] > self.temperature_threshold:
            self.consecutive_threshold_breaches += 1
            if self.consecutive_threshold_breaches >= 2:
                self.send_alert(weather_data)
        else:
            self.consecutive_threshold_breaches = 0

    def send_alert(self, weather_data):
        """Send alert for threshold breach"""
        message = f"ALERT: Temperature in {weather_data['city']} has exceeded {self.temperature_threshold}°C\n"
        message += f"Current temperature: {weather_data['temperature']:.1f}°C"
        
        print(message)  # For demonstration, just printing to console
        # Implement email notification here if needed

    def visualize_data(self, city):
        """Create visualizations of weather data"""
        # Get data from database
        query = f"""
            SELECT datetime(timestamp, 'unixepoch') as datetime, temperature
            FROM weather_data
            WHERE city = ?
            ORDER BY timestamp
        """
        df = pd.read_sql_query(query, self.conn, params=(city,))
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Create temperature trend plot
        plt.figure(figsize=(12, 6))
        plt.plot(df['datetime'], df['temperature'])
        plt.title(f'Temperature Trend - {city}')
        plt.xlabel('Time')
        plt.ylabel('Temperature (°C)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'temperature_trend_{city}.png')
        plt.close()

    def run(self, interval=300):  # interval in seconds (default 5 minutes)
        """Main loop to run the monitoring system"""
        try:
            while True:
                for city, coords in self.cities.items():
                    weather_data = self.get_weather_data(city, coords['lat'], coords['lon'])
                    if weather_data:
                        self.store_weather_data(weather_data)
                        self.check_temperature_threshold(weather_data)
                        self.calculate_daily_summary(city)
                        self.visualize_data(city)
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping weather monitoring system...")
            self.conn.close()

def main():
    # Create and run the weather monitoring system
    weather_system = WeatherMonitoringSystem()
    weather_system.run()

if __name__ == "__main__":
    main()


# In[ ]:


import unittest
from datetime import datetime
import os

class TestWeatherMonitoringSystem(unittest.TestCase):
    def setUp(self):
        self.weather_system = WeatherMonitoringSystem()

    def test_api_connection(self):
        """Test API connection and data retrieval"""
        city = "Delhi"
        coords = self.weather_system.cities[city]
        weather_data = self.weather_system.get_weather_data(city, coords['lat'], coords['lon'])
        
        self.assertIsNotNone(weather_data)
        self.assertEqual(weather_data['city'], city)
        self.assertIn('temperature', weather_data)
        self.assertIn('weather_condition', weather_data)

    def test_temperature_conversion(self):
        """Test Kelvin to Celsius conversion"""
        kelvin = 300
        celsius = self.weather_system.kelvin_to_celsius(kelvin)
        self.assertEqual(celsius, 26.85)

    def test_data_storage(self):
        """Test weather data storage in database"""
        test_data = {
            'city': 'TestCity',
            'temperature': 25.0,
            'feels_like': 26.0,
            'weather_condition': 'Clear',
            'timestamp': int(datetime.now().timestamp())
        }
        
        self.weather_system.store_weather_data(test_data)
        
        self.cursor.execute('''
            SELECT * FROM weather_data WHERE city = ? ORDER BY id DESC LIMIT 1
        ''', ('TestCity',))
        
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[1], 'TestCity')
        self.assertEqual(result[2], 25.0)

    def test_threshold_alert(self):
        """Test temperature threshold alerting"""
        test_data = {
            'city': 'TestCity',
            'temperature': 36.0,
            'feels_like': 38.0,
            'weather_condition': 'Clear',
            'timestamp': int(datetime.now().timestamp())
        }
        
        # Should trigger alert after two consecutive breaches
        self.weather_system.check_temperature_threshold(test_data)
        self.assertEqual(self.weather_system.consecutive_threshold_breaches, 1)
        
        self.weather_system.check_temperature_threshold(test_data)
        self.assertEqual(self.weather_system.consecutive_threshold_breaches, 2)

    def tearDown(self):
        self.weather_system.conn.close()
        os.remove('weather_data.db')

if __name__ == '__main__':
    unittest.main()

