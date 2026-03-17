import mysql.connector
import os
import webbrowser
import tempfile
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD', ''),
    database=os.getenv('MYSQL_DB', 'crime_db'),
    auth_plugin='mysql_native_password'
)
cursor = conn.cursor(dictionary=True)

cursor.execute("SHOW TABLES")
tables = [t[list(t.keys())[0]] for t in cursor.fetchall()]

def build_table_html(table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    if not rows:
        return f"<p class='empty'>No records in this table.</p>"
    cols = rows[0].keys()
    html = "<div class='table-wrap'><table><thead><tr>"
    for col in cols:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    for row in rows:
        html += "<tr>"
        for val in row:
            html += f"<td>{val if val is not None else '<span class=\"null\">NULL</span>'}</td>"
        html += "</tr>"
    html += f"</tbody></table></div><p class='count'>{len(rows)} row(s)</p>"
    return html

sections = ""
for tbl in tables:
    sections += f"""
    <section>
      <div class="table-header">
        <span class="table-icon">🗄️</span>
        <h2>{tbl}</h2>
      </div>
      {build_table_html(tbl)}
    </section>
    """

conn.close()

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>crime_data.db Viewer</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
    min-height: 100vh;
    padding: 2rem;
  }}
  header {{
    text-align: center;
    margin-bottom: 2.5rem;
  }}
  header h1 {{
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  header p {{ color: #94a3b8; margin-top: 0.4rem; font-size: 0.95rem; }}
  section {{
    background: rgba(30,41,59,0.6);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
  }}
  .table-header {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
  }}
  .table-icon {{ font-size: 1.3rem; }}
  h2 {{ font-size: 1.1rem; color: #93c5fd; letter-spacing: 0.05em; text-transform: uppercase; }}
  .table-wrap {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  thead {{ background: rgba(59,130,246,0.15); }}
  th {{
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    color: #7dd3fc;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    white-space: nowrap;
  }}
  td {{
    padding: 0.65rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    color: #cbd5e1;
    white-space: nowrap;
  }}
  tr:hover td {{ background: rgba(255,255,255,0.04); }}
  .null {{ color: #475569; font-style: italic; font-size: 0.8rem; }}
  .count {{ color: #64748b; font-size: 0.8rem; margin-top: 0.75rem; text-align: right; }}
  .empty {{ color: #475569; font-style: italic; padding: 1rem 0; }}
  .db-path {{
    display: inline-block;
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 6px;
    padding: 0.3rem 0.8rem;
    font-family: monospace;
    font-size: 0.85rem;
    color: #60a5fa;
    margin-top: 0.5rem;
  }}
</style>
</head>
<body>
  <header>
    <h1>🔍 Database Viewer</h1>
    <p>Live snapshot of your MySQL database</p>
    <span class="db-path">MYSQL Database: {os.getenv('MYSQL_DB', 'crime_db')} on {os.getenv('MYSQL_HOST', 'localhost')}</span>
  </header>
  {sections}
</body>
</html>"""

tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
tmp.write(html)
tmp.close()

webbrowser.open(f"file:///{tmp.name}")
print(f"Opened DB viewer in browser: {tmp.name}")
