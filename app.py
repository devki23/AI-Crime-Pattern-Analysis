from flask import Flask, jsonify, request, render_template
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
import os
from dotenv import load_dotenv

from backend.app.services.database import get_db_connection
import pandas as pd
import random
import math
import numpy as np
import simplejson
from flask.json.provider import DefaultJSONProvider
from decimal import Decimal
from datetime import datetime, date

class CustomJSONProvider(DefaultJSONProvider):
    def dumps(self, obj, **kwargs):
        def default_encoder(o):
            if hasattr(o, 'strftime'):
                return o.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(o, Decimal):
                return float(o)
            from datetime import timedelta
            if isinstance(o, timedelta):
                return str(o)
            # Try to get __dict__ or fall back
            if hasattr(o, '__dict__'):
                return o.__dict__
            return str(o)
            
        kwargs.setdefault('ignore_nan', True)
        kwargs.setdefault('default', default_encoder)
        return simplejson.dumps(obj, **kwargs)

    def loads(self, s, **kwargs):
        return simplejson.loads(s, **kwargs)

# Use default Flask JSON provider
app = Flask(__name__, 
            static_folder='frontend/static',
            template_folder='frontend/templates')

app.json = CustomJSONProvider(app)

CORS(app)

# Default configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'crime-pattern-dev-key')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard_page():
    return render_template('admin_dashboard.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'officer')
    phone = data.get('phone')
    station = data.get('station')
    username = data.get('username')
    badge_number = data.get('badge')
    aadhar_number = data.get('aadhar_number', '').strip()

    # Block admin self-registration — admins are created by system only
    if role == 'admin':
        return jsonify({"status": "error", "message": "Admin registration is not allowed. Contact system administrator."}), 403

    # Basic validation
    missing_fields = []
    if not full_name: missing_fields.append("full_name")
    if not email: missing_fields.append("email")
    if not password: missing_fields.append("password")
    if not role: missing_fields.append("role")
    if not username: missing_fields.append("username")

    # Aadhar validation for officers
    if not aadhar_number:
        return jsonify({"status": "error", "message": "Aadhar Card Number is required for officer registration."}), 400
    if not aadhar_number.isdigit() or len(aadhar_number) != 12:
        return jsonify({"status": "error", "message": "Aadhar Card Number must be exactly 12 digits."}), 400

    # Password Validation
    if password:
        if len(password) < 8:
            return jsonify({"status": "error", "message": "Password must be at least 8 characters long"}), 400
        if not password[0].isupper():
            return jsonify({"status": "error", "message": "Password must start with a capital letter"}), 400

    if missing_fields:
        print(f"DEBUG: Failed registration. Received: {data}")
        return jsonify({"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO users (full_name, email, password, role, phone, station, badge_number, username, aadhar_number, approval_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (full_name, email, password, role, phone, station, badge_number, username, aadhar_number, 'pending')
        )
        connection.commit()
        return jsonify({"status": "success", "message": "Registration submitted! Awaiting admin approval. You will be notified once approved."}), 201
    except Exception as e:
        err = str(e)
        if "users.email" in err:
            return jsonify({"status": "error", "message": "Email already exists"}), 409
        elif "users.username" in err:
            return jsonify({"status": "error", "message": "Officer ID / Username already exists"}), 409
        else:
            return jsonify({"status": "error", "message": f"Account with this Email or Officer ID already exists"}), 409
    finally:
        connection.close()

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    identifier = data.get('email') or data.get('username')
    password = data.get('password')
    requested_role = data.get('role')
    aadhar_number = data.get('aadhar_number', '').strip()

    print(f"DEBUG: Login attempt for identifier: {identifier}, role: {requested_role}")

    if not all([identifier, password]):
        return jsonify({"status": "error", "message": "Missing credentials"}), 400

    # For officer login, Aadhar is required
    if requested_role == 'officer':
        if not aadhar_number:
            return jsonify({"status": "error", "message": "Aadhar Card Number is required for officer login."}), 400
        if not aadhar_number.isdigit() or len(aadhar_number) != 12:
            return jsonify({"status": "error", "message": "Aadhar Card Number must be exactly 12 digits."}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        print(f"DEBUG: Querying database for user...")
        cursor.execute("SELECT * FROM users WHERE (email = %s OR username = %s) AND password = %s", (identifier, identifier, password))
        user = cursor.fetchone()

        if user:
            # Check approval status for officers
            if user['role'] == 'officer':
                approval = user.get('approval_status') or 'approved'
                # None/NULL means old account = approved by default
                # Only block if explicitly 'pending' or 'rejected'
                if approval == 'pending':
                    return jsonify({"status": "error", "message": "⏳ Your account is pending admin approval. Please wait for admin to approve your registration."}), 403
                if approval == 'rejected':
                    return jsonify({"status": "error", "message": "❌ Your registration has been rejected by the administrator. Please contact HQ."}), 403

            # Validate role match
            if requested_role and user['role'] != requested_role:
                print(f"DEBUG: Role mismatch. User is {user['role']}, requested {requested_role}")
                return jsonify({"status": "error", "message": f"Access Denied: You cannot login as {requested_role.capitalize()} with this account."}), 403

            # For officers: verify Aadhar number matches DB record
            if user['role'] == 'officer':
                stored_aadhar = (user.get('aadhar_number') or '').strip()
                if stored_aadhar and stored_aadhar != aadhar_number:
                    print(f"DEBUG: Aadhar mismatch for user: {user['username']}")
                    return jsonify({"status": "error", "message": "Invalid Aadhar Card number. Access denied."}), 403

            print(f"DEBUG: Login success for user: {user['username']}")
            return jsonify({
                "status": "success",
                "user": {
                    "user_id": user['user_id'],
                    "full_name": user['full_name'],
                    "role": user['role'],
                    "username": user['username']
                }
            }), 200
        else:
            cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", (identifier, identifier))
            user_exists = cursor.fetchone()
            if user_exists:
                print(f"DEBUG: User found but password mismatch.")
            else:
                print(f"DEBUG: User not found with identifier: {identifier}")
            return jsonify({"status": "error", "message": "Invalid username/email or password"}), 401
    except Exception as e:
        print(f"DEBUG: Login error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/auth/password/update', methods=['POST'])
def update_password():
    data = request.json
    user_id = data.get('user_id')
    email = data.get('email') # Fallback
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not (user_id or email) or not current_password or not new_password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
        
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verify current password
        if user_id:
             cursor.execute("SELECT user_id FROM users WHERE user_id = %s AND password = %s", (user_id, current_password))
        else:
             cursor.execute("SELECT user_id FROM users WHERE email = %s AND password = %s", (email, current_password))

        user = cursor.fetchone()
        
        if not user:
            return jsonify({"status": "error", "message": "Invalid current password"}), 401
            
        # Update password
        cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password, user['user_id']))
        connection.commit()
        
        return jsonify({"status": "success", "message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()


@app.route('/api/crimes/submit', methods=['POST'])
def submit_crime():
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        INSERT INTO crimes 
        (crime_id, crime_type, description, occurrence_date, latitude, longitude, location_description, arrested)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        crime_id = f"C{random.randint(200000, 999999)}"
        values = (
            crime_id, data['type'], data['description'], 
            data['date'], data['lat'], data['lng'],
            data['location'], 0
        )
        cursor.execute(query, values)
        connection.commit()
        return jsonify({"status": "success", "crime_id": crime_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "crime-analysis-api", "database": "sqlite"}), 200

@app.route('/api/version', methods=['GET'])
def version_check():
    return "VERIFIED_FIX_V2", 200


def clean_nans(data):
    if data is None:
        return None
    elif isinstance(data, (int, str, bool)):
        return data
    elif isinstance(data, float):
        if math.isnan(data) or np.isnan(data):
            return None
        return data
    elif hasattr(data, 'strftime'):
        return data.strftime('%Y-%m-%d %H:%M:%S')
    from decimal import Decimal
    if isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, dict):
        return {k: clean_nans(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_nans(v) for v in data]
    else:
        # Fallback for unexpected pandas types like pd.Timestamp or np.int64
        return str(data)

@app.route('/api/crimes', methods=['GET'])
def get_crimes():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM crimes ORDER BY occurrence_date DESC")
        rows = cursor.fetchall()

        # Iterate via raw dictionary rows to avoid pandas Timestamp injection
        for row in rows:
            for key, val in row.items():
                if hasattr(val, 'strftime'):
                    row[key] = val.strftime('%Y-%m-%d %H:%M:%S')
                # MySQL connector can also return bytearrays or timedelta for some fields
                elif val is not None and not isinstance(val, (int, float, str, bool)):
                    row[key] = str(val)

        # Apply fallback missing data cleaning
        crimes = clean_nans(rows)

        return jsonify({"crimes": crimes, "count": len(crimes)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/crimes/<crime_id>', methods=['DELETE'])
def delete_crime(crime_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("DELETE FROM crimes WHERE crime_id = %s", (crime_id,))
        connection.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/crimes/<crime_id>', methods=['PUT'])
def update_crime(crime_id):
    connection = get_db_connection()
    if not connection:
         return jsonify({"error": "Database connection failed"}), 500
    try:
        data = request.json
        # Handle status toggle specifically if requested
        if 'status' in data:
             new_status = 1 if data['status'] == 'closed' else 0
             cursor = connection.cursor(dictionary=True)
             cursor.execute("UPDATE crimes SET arrested = %s WHERE crime_id = %s", (new_status, crime_id))
             connection.commit()
             return jsonify({"status": "success", "message": "Status updated"}), 200
        
        # Handle general update
        crime_type = data.get('crime_type')
        description = data.get('description')
        location = data.get('location_description')
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            UPDATE crimes 
            SET crime_type = %s, description = %s, location_description = %s
            WHERE crime_id = %s
        """, (crime_type, description, location, crime_id))
        connection.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/hotspots', methods=['GET'])
def get_hotspots():
    model = HotspotModel(n_clusters=10)
    centers = model.get_hotspots()
    if centers is not None:
        hotspots = []
        for c in centers:
             lat = float(c[0])
             lng = float(c[1])
             if not (math.isnan(lat) or math.isnan(lng)):
                 hotspots.append({"lat": lat, "lng": lng})
        return jsonify({"hotspots": hotspots}), 200
    return jsonify({"error": "Could not generate hotspots"}), 500

@app.route('/hotspot-map')
def hotspot_map():
    import folium
    from sklearn.cluster import KMeans

    # Try to get real crime data from the DB
    connection = get_db_connection()
    rows = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT latitude, longitude FROM crimes WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
            rows = cursor.fetchall()
        except Exception:
            pass
        finally:
            connection.close()

    if len(rows) >= 3:
        data = pd.DataFrame(rows, columns=['latitude', 'longitude'])
    else:
        # Fallback sample data (Surat region)
        data = pd.DataFrame({
            'latitude': [21.2002, 21.1710, 21.1805, 21.1750, 21.1680, 21.1695, 22.1415],
            'longitude': [72.8595, 72.8320, 72.8403, 72.8350, 72.8300, 72.8335, 72.8345]
        })

    n_clusters = min(3, len(data))
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(data[['latitude', 'longitude']])
    data['cluster'] = kmeans.labels_.astype(int)
    centers = kmeans.cluster_centers_

    map_center = [data['latitude'].mean(), data['longitude'].mean()]
    crime_map = folium.Map(location=map_center, zoom_start=17, tiles='CartoDB positron')
    colors = ['red', 'green', 'blue', 'orange', 'purple']

    for _, row in data.iterrows():
        c = int(row['cluster'])
        folium.CircleMarker(
            location=(row['latitude'], row['longitude']),
            radius=8,
            color=colors[c % len(colors)],
            fill=True,
            fill_color=colors[c % len(colors)],
            fill_opacity=0.75,
            popup=folium.Popup(f"<b>Crime Point</b><br>Cluster {c + 1}", max_width=200)
        ).add_to(crime_map)

    for i, center in enumerate(centers):
        folium.Marker(
            location=(center[0], center[1]),
            icon=folium.Icon(color='black', icon='info-sign'),
            popup=folium.Popup(f"<b>🔴 Hotspot Center {i + 1}</b><br>AI-identified high-risk zone", max_width=200)
        ).add_to(crime_map)

    return crime_map.get_root().render()

@app.route('/api/admin/users', methods=['GET'])
def get_users():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id as id, username, email, full_name, role, created_at, approval_status, aadhar_number FROM users")
        
        rows = cursor.fetchall()

        users_clean = []
        for row in rows:
            clean_row = {}
            for key, val in row.items():
                if hasattr(val, 'strftime'):
                    clean_row[key] = val.strftime('%Y-%m-%d %H:%M:%S')
                elif val is None:
                    clean_row[key] = None
                elif isinstance(val, (int, float, str, bool)):
                    clean_row[key] = val
                else:
                    clean_row[key] = str(val)
            users_clean.append(clean_row)

        users = clean_nans(users_clean)
        return jsonify({"users": users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        connection.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        data = request.json
        full_name = data.get('full_name')
        email = data.get('email')
        role = data.get('role')
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            UPDATE users 
            SET full_name = %s, email = %s, role = %s
            WHERE user_id = %s
        """, (full_name, email, role, user_id))
        connection.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/admin/db-reset', methods=['POST'])
def reset_database():
    try:
        from backend.app.services.database import init_db
        from scripts.load_data import generate_sample_data, insert_to_mysql
        
        # 1. Initialize Schema
        init_db()

        # 2. Seed Users
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO users (username, full_name, email, password, role, station, badge_number)
                VALUES 
                ('admin', 'System Administrator', 'admin@police.gov', 'admin123', 'admin', 'Headquarters', 'ADM-001'),
                ('officer', 'Officer Sharma', 'officer@police.gov', 'police123', 'officer', 'Rohini Sector 16', 'POL-102')
            """)
            connection.commit()
            connection.close()

        # 3. Seed Crimes
        sample_data = generate_sample_data(200)
        insert_to_mysql(sample_data)
        
        return jsonify({"status": "success", "message": "Database reset and re-seeded with Users & 200 Crimes."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/analysis', methods=['GET'])
def admin_analysis():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        # 1. Get total crime count & open cases
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) FROM crimes")
        total_crimes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM crimes WHERE arrested = 0")
        cursor.execute("SELECT COUNT(*) FROM crimes WHERE arrested = 0")
        open_cases = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users")
        total_officers = cursor.fetchone()[0]

        # 2. Identify Hotspot (Most frequent location description in last 50 recs)
        # We use a simple frequency check on 'location_description' or 'crime_type'
        cursor.execute("SELECT COUNT(*) FROM (SELECT location_description FROM crimes GROUP BY location_description HAVING COUNT(*) > 3)")
        hotspot_count_val = cursor.fetchone()[0]

        # Get top hotspot for text
        query = """
            SELECT location_description, COUNT(*) as count 
            FROM crimes 
            GROUP BY location_description 
            ORDER BY count DESC 
            LIMIT 1
        """
        cursor.execute(query)
        hotspot_row = cursor.fetchone()
        
        if hotspot_row:
            location = hotspot_row[0]
            count = hotspot_row[1]
            analysis_text = f"Hotspot detected near {location} with {count} reported cases."
            analysis_type = "Critical" if count > 5 else "Moderate"
        else:
            analysis_text = "No sufficient data to identify hotspots yet."
            analysis_type = "Low"

        return jsonify({
            "total_crimes": total_crimes,
            "open_cases": open_cases,
            "total_officers": total_officers,
            "total_officers": total_officers,
            "hotspot_count": hotspot_count_val,
            "latest_analysis": {
                "text": analysis_text,
                "type": analysis_type
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/admin/detailed-analysis', methods=['GET'])
def admin_detailed_analysis():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. High Priority Hotspots (Top 5 Areas by Crime Count)
        cursor.execute("SELECT location_description, COUNT(*) as count FROM crimes GROUP BY location_description ORDER BY count DESC LIMIT 5")
        hotspots = [{"area": row[0], "count": row[1]} for row in cursor.fetchall()]

        # 2. Crime Type Distribution
        cursor.execute("SELECT crime_type, COUNT(*) as count FROM crimes GROUP BY crime_type")
        type_data = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]
        total_crimes = sum(item['count'] for item in type_data)
        type_distribution = []
        if total_crimes > 0:
            type_distribution = [{"type": item['type'], "percentage": round((item['count'] / total_crimes) * 100)} for item in type_data]
            type_distribution.sort(key=lambda x: x['percentage'], reverse=True)

        # 3. Time Patterns
        cursor.execute("SELECT strftime('%H', occurrence_date), COUNT(*) FROM crimes GROUP BY strftime('%H', occurrence_date)")
        time_raw = cursor.fetchall()
        
        time_counts = {'Morning (4AM-12PM)': 0, 'Afternoon (12PM-6PM)': 0, 'Evening (6PM-11PM)': 0, 'Night (11PM-4AM)': 0}
        for hour_str, count in time_raw:
            if hour_str:
                h = int(hour_str)
                if 4 <= h < 12: time_counts['Morning (4AM-12PM)'] += count
                elif 12 <= h < 18: time_counts['Afternoon (12PM-6PM)'] += count
                elif 18 <= h < 23: time_counts['Evening (6PM-11PM)'] += count
                else: time_counts['Night (11PM-4AM)'] += count
        
        time_patterns = []
        if total_crimes > 0:
            for k, v in time_counts.items():
                time_patterns.append({"time": k, "percentage": round((v / total_crimes) * 100)})
            time_patterns.sort(key=lambda x: x['percentage'], reverse=True)

        # 4. AI Insights
        insights = []
        if type_distribution:
            top_crime = type_distribution[0]
            insights.append({
                "title": f"{top_crime['type'].title()} Pattern Detected",
                "icon": "fa-lightbulb",
                "color_class": "text-yellow-500", 
                "text": f"High concentration of {top_crime['type'].lower()} ({top_crime['percentage']}%) detected."
            })
        
        if time_patterns:
            peak = time_patterns[0]
            insights.append({
                "title": "Peak Activity Time",
                "icon": "fa-clock",
                "color_class": "text-cyan-500",
                "text": f"Crime reporting peaks during {peak['time'].split('(')[0].lower()} ({peak['percentage']}%)."
            })

        if hotspots:
            top = hotspots[0]
            insights.append({
                "title": "Emerging Hotspot",
                "icon": "fa-map-marker-alt",
                "color_class": "text-red-500",
                "text": f"{top['area']} shows high incident frequency ({top['count']} cases)."
            })

        return jsonify({
            "hotspots": hotspots,
            "type_distribution": type_distribution,
            "time_patterns": time_patterns,
            "insights": insights
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/predict/safety', methods=['GET'])
def predict_safety():
    area = request.args.get('area', 'General').strip().title()
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        import requests
        import xml.etree.ElementTree as ET

        # Fix: correct RSS URL (was %sq= which is wrong)
        rss_url = f"https://news.google.com/rss/search?q={area}+crime+india&hl=en-IN&gl=IN&ceid=IN:en"
        news_count = 0
        sentiment_score = 0

        try:
            response = requests.get(rss_url, timeout=5)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                items = root.findall('.//item')
                news_count = len(items)
                high_risk_keywords = ['murder', 'arrest', 'killed', 'theft', 'robbery', 'scam', 'fraud', 'rape', 'death']
                for item in items[:15]:
                    title_el = item.find('title')
                    if title_el is not None and title_el.text:
                        if any(word in title_el.text.lower() for word in high_risk_keywords):
                            sentiment_score += 1
        except Exception as e:
            print(f"Internet fetching error: {e}")
            news_count = 0

        # Query local DB for crimes in this area
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(*) as cnt FROM crimes WHERE location_description LIKE %s",
            (f"%{area}%",)
        )
        local_row = cursor.fetchone()
        local_crime_count = local_row['cnt'] if local_row else 0

        # Score calculation: base 9.5, penalties reduce it
        base_score = 9.5
        news_penalty = news_count * 0.1
        keyword_penalty = sentiment_score * 0.3
        local_penalty = min(local_crime_count * 0.05, 3.0)

        city_baseline = 0.0
        area_lower = area.lower()
        if any(c in area_lower for c in ['delhi', 'mumbai']): city_baseline = -1.5
        elif any(c in area_lower for c in ['bangalore', 'pune', 'hyderabad']): city_baseline = -0.8
        elif any(c in area_lower for c in ['surat', 'ahmedabad', 'vadodara']): city_baseline = -0.5

        score = round(max(1.5, min(9.9, base_score - news_penalty - keyword_penalty - local_penalty + city_baseline)), 1)
        
        label = "Safe Zone"
        if score < 4.5: label = "High Alert - Heavy News Activity"
        elif score < 7.5: label = "Moderate Risk - Recent Incidents Reported"
        else: label = "Safe Zone - Low News Density"
        
        return jsonify({
            "area": area,
            "score": score,
            "label": label,
            "incidents_analyzed": news_count,
            "source": "Live Google News (Real-time)",
            "summary": f"Analyzed {news_count} recent reports for {area}. Sentiment weighted: {sentiment_score}."
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/admin/reports/download/<report_type>', methods=['GET'])
def download_report(report_type):
    connection = get_db_connection()
    if not connection:
        return "Database connection failed", 500
    
    try:
        import io
        import csv
        from flask import Response

        if report_type == 'all_crimes':
            # Generate CSV of all crimes
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM crimes ORDER BY occurrence_date DESC")
            cols = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(cols)
            writer.writerows(rows)
            
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-disposition": "attachment; filename=all_crimes_report.csv"}
            )
            
        elif report_type == 'officer_performance':
            # Generate CSV of officers
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT user_id, full_name, username, email, role, station, badge_number FROM users WHERE role != 'admin'")
            cols = ["ID", "Name", "Username", "Email", "Role", "Station", "Badge"]
            rows = cursor.fetchall()
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(cols)
            writer.writerows(rows)
            
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-disposition": "attachment; filename=officer_performance.csv"}
            )
            
        elif report_type == 'monthly_summary':
             # Generate Text Summary
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) FROM crimes")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT crime_type, COUNT(*) as c FROM crimes GROUP BY crime_type ORDER BY c DESC LIMIT 5")
            top_crimes = cursor.fetchall()
            
            output = io.StringIO()
            output.write("CRIME PATTERN ANALYSIS - MONTHLY SUMMARY\n")
            output.write("========================================\n\n")
            output.write(f"Total Reported Crimes: {total}\n\n")
            output.write("Top Crime Types:\n")
            for row in top_crimes:
                output.write(f"- {row[0]}: {row[1]} cases\n")
                
            output.write("\nEnd of Report.\n")
            
            return Response(
                output.getvalue(),
                mimetype="text/plain",
                headers={"Content-disposition": "attachment; filename=monthly_crime_summary.txt"}
            )

        else:
            return "Invalid Report Type", 400

    except Exception as e:
        return f"Error generating report: {str(e)}", 500
    finally:
        connection.close()

@app.route('/api/admin/users/<int:user_id>/approve', methods=['POST'])
def approve_user(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("UPDATE users SET approval_status = 'approved' WHERE user_id = %s", (user_id,))
        connection.commit()
        return jsonify({"status": "success", "message": "Officer approved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/admin/users/<int:user_id>/reject', methods=['POST'])
def reject_user(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("UPDATE users SET approval_status = 'rejected' WHERE user_id = %s", (user_id,))
        connection.commit()
        return jsonify({"status": "success", "message": "Officer rejected"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/admin/pending-officers', methods=['GET'])
def get_pending_officers():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id as id, username, full_name, email, phone, station, 
                   badge_number, aadhar_number, created_at, approval_status 
            FROM users 
            WHERE role = 'officer' AND approval_status = 'pending'
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        officers = []
        for row in rows:
            clean = {}
            for key, val in row.items():
                if hasattr(val, 'strftime'):
                    clean[key] = val.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    clean[key] = val
            officers.append(clean)
        return jsonify({"pending_officers": officers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/db-viewer')
def db_viewer():
    connection = get_db_connection()
    if not connection:
        return "<h2>Database connection failed</h2>", 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [t[0] for t in cursor.fetchall()]

    sections = ""
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            cols = rows[0].keys() if rows else []
            thead = "".join(f"<th>{c}</th>" for c in cols)
            tbody = ""
            for row in rows:
                cells = "".join(f"<td>{'<span class=\"null\">NULL</span>' if v is None else v}</td>" for v in row)
                tbody += f"<tr>{cells}</tr>"
            count = len(rows)
            sections += f"""
            <section>
              <div class="th"><span>🗄️</span><h2>{table} <small>({count} rows)</small></h2></div>
              <div class="tw"><table><thead><tr>{thead}</tr></thead><tbody>{tbody if tbody else '<tr><td colspan="99" class="empty">No records</td></tr>'}</tbody></table></div>
            </section>"""
        except Exception as e:
            sections += f"<section><p>Error reading {table}: {e}</p></section>"

    connection.close()

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>DB Viewer — crime_data.db</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#0f172a,#1e293b);color:#f1f5f9;min-height:100vh;padding:2rem}}
header{{text-align:center;margin-bottom:2rem}}
header h1{{font-size:2rem;font-weight:700;background:linear-gradient(135deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
header p{{color:#94a3b8;font-size:.9rem;margin-top:.3rem}}
.badge{{display:inline-block;background:rgba(59,130,246,.1);border:1px solid rgba(59,130,246,.3);border-radius:6px;padding:.2rem .7rem;font-family:monospace;color:#60a5fa;font-size:.8rem;margin-top:.5rem}}
section{{background:rgba(30,41,59,.6);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;backdrop-filter:blur(10px)}}
.th{{display:flex;align-items:center;gap:.6rem;margin-bottom:1rem}}
.th span{{font-size:1.2rem}}
h2{{font-size:1rem;color:#93c5fd;text-transform:uppercase;letter-spacing:.05em}}
h2 small{{font-size:.75rem;color:#475569;text-transform:none;letter-spacing:0}}
.tw{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:.85rem}}
thead{{background:rgba(59,130,246,.12)}}
th{{padding:.6rem 1rem;text-align:left;color:#7dd3fc;font-weight:600;white-space:nowrap;border-bottom:1px solid rgba(255,255,255,.1)}}
td{{padding:.55rem 1rem;border-bottom:1px solid rgba(255,255,255,.05);color:#cbd5e1;white-space:nowrap}}
tr:hover td{{background:rgba(255,255,255,.03)}}
.null{{color:#475569;font-style:italic;font-size:.8rem}}
.empty{{color:#475569;font-style:italic;text-align:center;padding:1rem}}
.refresh{{display:inline-block;margin-top:1rem;background:linear-gradient(135deg,#3b82f6,#2563eb);color:white;padding:.5rem 1.2rem;border-radius:8px;text-decoration:none;font-size:.9rem;font-weight:600}}
.refresh:hover{{opacity:.85}}
</style></head>
<body>
<header>
  <h1>🔍 Database Viewer</h1>
  <p>Live view of your SQLite database</p>
  <div class="badge">crime_data.db</div><br>
  <a href="/db-viewer" class="refresh">🔄 Refresh</a>
</header>
{sections}
</body></html>"""
    return html


if __name__ == '__main__':

    port = int(os.getenv('PORT', 5000))
    print("\n" + "="*50)
    print("SERVER STARTED SUCCESSFULLY - PLEASE RELOAD DASHBOARD")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=port, debug=True)