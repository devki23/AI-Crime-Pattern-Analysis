import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

csv_data = """crime_id,crime_type,date,time,city,area,latitude,longitude,description
1,Theft,2024-01-05,21:10,Ahmedabad,Navrangpura,23.0330,72.5560,Bike stolen outside cafe
2,Robbery,2024-01-07,19:40,Surat,Adajan,21.1702,72.8311,Mobile snatching
3,Assault,2024-01-09,14:25,Vadodara,Alkapuri,22.3072,73.1812,Street fight
4,Burglary,2024-01-12,02:15,Rajkot,Raiya,22.3039,70.8022,House break-in
5,Vehicle Theft,2024-01-14,23:55,Ahmedabad,Bopal,23.0328,72.4700,Car missing
6,Cyber Crime,2024-01-18,11:30,Surat,Vesu,21.1500,72.7800,Online scam
7,Drug Offense,2024-01-20,18:05,Vadodara,Manjalpur,22.2780,73.2000,Suspicious dealing
8,Domestic Violence,2024-01-24,21:45,Rajkot,Kuvadva Road,22.2900,70.8200,Complaint filed
9,Theft,2024-02-01,17:25,Ahmedabad,Satellite,23.0270,72.5100,Phone stolen
10,Robbery,2024-02-03,20:50,Surat,Katargam,21.2300,72.8300,Street robbery
11,Assault,2024-02-06,15:10,Vadodara,Gorwa,22.3300,73.1500,Public fight
12,Burglary,2024-02-08,03:20,Rajkot,Kalavad Road,22.3100,70.7800,Shop break-in
13,Vehicle Theft,2024-02-11,22:35,Ahmedabad,Thaltej,23.0490,72.5120,Bike missing
14,Cyber Crime,2024-02-15,12:40,Surat,Udhna,21.1700,72.8400,UPI fraud
15,Drug Offense,2024-02-18,19:30,Vadodara,Fatehgunj,22.3200,73.1900,Illegal substances found
16,Domestic Violence,2024-02-22,21:10,Rajkot,Mavdi,22.2700,70.8000,Family dispute
17,Theft,2024-03-02,16:50,Ahmedabad,Maninagar,23.0010,72.6000,Wallet stolen
18,Robbery,2024-03-05,21:30,Surat,Piplod,21.1400,72.7800,Snatching incident
19,Assault,2024-03-08,13:20,Vadodara,Akota,22.2900,73.1700,Argument turned violent
20,Burglary,2024-03-10,01:40,Rajkot,Yagnik Road,22.3000,70.7900,Office break-in"""

def insert_data():
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'crime_db'),
        auth_plugin='mysql_native_password'
    )
    cursor = conn.cursor()

    lines = csv_data.strip().split('\n')
    header = lines[0]
    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) >= 9:
            crime_id = f"CR-{parts[0].strip()}"
            crime_type = parts[1].strip()
            date = parts[2].strip()
            time = parts[3].strip()
            occurrence_date = f"{date} {time}:00"
            city = parts[4].strip()
            area = parts[5].strip()
            location_desc = f"{area}, {city}"
            lat = float(parts[6].strip())
            lng = float(parts[7].strip())
            desc = parts[8].strip()
            
            # Combine the description with the short CSV description to give better context
            full_desc = f"{desc} | Location: {location_desc}"

            sql = """
            INSERT INTO crimes (crime_id, crime_type, description, occurrence_date, latitude, longitude, location_description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                crime_type=VALUES(crime_type), 
                description=VALUES(description), 
                occurrence_date=VALUES(occurrence_date), 
                latitude=VALUES(latitude), 
                longitude=VALUES(longitude), 
                location_description=VALUES(location_description)
            """
            cursor.execute(sql, (crime_id, crime_type, full_desc, occurrence_date, lat, lng, location_desc))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Data inserted successfully.")

if __name__ == "__main__":
    insert_data()
