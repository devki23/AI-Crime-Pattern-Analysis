# AI-Powered Crime Pattern Analysis System

## Overview
The AI-Powered Crime Pattern Analysis System is a web-based application designed to help law enforcement agencies store, manage, and analyze crime data. The system uses machine learning techniques to detect crime patterns and identify high-risk areas (crime hotspots).

This project allows police officers to record crime incidents and provides administrators with analytics and visualization tools to better understand crime trends.

---

## Features

- Officer Registration and Secure Login
- Admin Approval System for Officers
- Crime Incident Reporting
- Interactive Crime Dashboard
- Crime Data Visualization
- AI-Based Crime Hotspot Detection
- Map Visualization using Leaflet
- Crime Statistics and Reports
- Admin Panel for System Management

---

## Technologies Used

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask Framework

### Database
- MySQL

### Machine Learning
- K-Means Clustering Algorithm (Scikit-learn)

### Tools
- VS Code
- GitHub
- XAMPP / MySQL Server

---

## System Architecture

1. Police officers log into the system.
2. Officers submit crime reports including location and description.
3. Crime data is stored in the MySQL database.
4. The system analyzes crime locations using K-Means clustering.
5. Crime hotspots are displayed on an interactive map.
6. Admin dashboard provides statistics and system insights.

---

## Key Modules

### 1. Authentication Module
Allows officers and administrators to securely log into the system.

### 2. Crime Reporting Module
Officers can add crime details such as crime type, location, coordinates, date, and description.

### 3. Crime Analysis Module
Machine learning algorithms analyze crime location data to detect clusters and hotspots.

### 4. Map Visualization Module
Crime locations and hotspots are displayed on an interactive map.

### 5. Admin Dashboard
Provides overview statistics including total crimes, officers, open cases, and detected hotspots.

---

## AI Component

The system uses the **K-Means Clustering Algorithm** to analyze the geographical coordinates of crime incidents. This helps identify areas with a high concentration of crimes.

These identified clusters represent **crime hotspots**, which can help authorities take preventive measures and allocate resources more effectively.

---

## Installation Steps

1. Install required Python libraries: pip install -r requirements.txt
2. Configure the database (MySQL)
3. Run the application: python app.py
4. Open browser: http://127.0.0.1:5000

---

## Future Enhancements

- Real-time crime data integration
- Advanced predictive analytics
- Crime heatmap visualization
- Mobile application for officers
- Integration with government crime databases

---

## Conclusion

The AI-Powered Crime Pattern Analysis System demonstrates how artificial intelligence and data analysis can help law enforcement agencies better understand crime patterns and improve public safety.

---

## Author

Devki Prajapati  
BCA (Hons) – GLS University  
Capstone Project

