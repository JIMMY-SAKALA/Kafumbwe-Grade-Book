import os
import sqlite3
import http.server
import socketserver
import urllib.parse

# Initialize database with tables for Teachers, Classes, Students, Results
def init_db():
    conn = sqlite3.connect("gradesystem.db")
    cursor = conn.cursor()

    # Drop tables if they exist
    cursor.executescript("""
    DROP TABLE IF EXISTS Teachers;
    DROP TABLE IF EXISTS Class;
    DROP TABLE IF EXISTS Student;
    DROP TABLE IF EXISTS Results;
    """)

    # Create tables in specified order
    cursor.execute("""
    -- Teachers table
    CREATE TABLE Teachers (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE,
        Password TEXT,
        Role TEXT -- 'teacher' or 'pupil'
    );
    """)
    cursor.execute("""
    -- Classes table
    CREATE TABLE Class (
        ClassID INTEGER PRIMARY KEY AUTOINCREMENT,
        ClassName TEXT UNIQUE
    );
    """)
    cursor.execute("""
    -- Students table
    CREATE TABLE Student (
        StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
        ExamNumber TEXT,
        Name TEXT,
        ClassID INTEGER,
        FOREIGN KEY (ClassID) REFERENCES Class(ClassID)
    );
    """)
    cursor.execute("""
    -- Results table
    CREATE TABLE Results (
        ResultID INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentID INTEGER,
        Subject TEXT,
        Score INTEGER,
        Term TEXT,
        TeacherID INTEGER,
        FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
        FOREIGN KEY (TeacherID) REFERENCES Teachers(UserID)
    );
    """)

    # Insert sample data
    cursor.execute("INSERT OR IGNORE INTO Teachers (Username, Password, Role) VALUES ('Ms Mpongwe', 'pass123', 'teacher')")
    cursor.execute("INSERT OR IGNORE INTO Teachers (Username, Password, Role) VALUES ('Mr Zulu', 'pass123', 'teacher')")
    cursor.execute("INSERT OR IGNORE INTO Teachers (Username, Password, Role) VALUES ('Madam Kalenga', 'pass123', 'teacher')")
    cursor.execute("INSERT OR IGNORE INTO Teachers (Username, Password, Role) VALUES ('Mr Sakala', 'pass123', 'teacher')")
    cursor.execute("INSERT OR IGNORE INTO Teachers (Username, Password, Role) VALUES ('pupil1', 'pass123', 'pupil')")
    cursor.execute("INSERT OR IGNORE INTO Teachers (Username, Password, Role) VALUES ('pupil2', 'pass123', 'pupil')")

    cursor.execute("INSERT OR IGNORE INTO Class (ClassName) VALUES ('Form 1')")
    cursor.execute("INSERT OR IGNORE INTO Class (ClassName) VALUES ('Form 2')")
    cursor.execute("INSERT OR IGNORE INTO Class (ClassName) VALUES ('Form 3')")
    cursor.execute("INSERT OR IGNORE INTO Class (ClassName) VALUES ('Form 4')")
    cursor.execute("INSERT OR IGNORE INTO Class (ClassName) VALUES ('Form 5')")

    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (001, 'Alice', 1)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (2026, 'Jane', 1)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (002, 'Bob', 2)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (2002, 'Zack', 2)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (1709, 'Jimmy Sakala', 3)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (2020, 'Charlie Sakala', 3)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (2023, 'James Sakala', 4)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (008, 'Dee', 4)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (2050, 'Kennedy', 5)")
    cursor.execute("INSERT OR IGNORE INTO Student (ExamNumber, Name, ClassID) VALUES (1999, 'Ben', 5)") 

    cursor.execute("INSERT OR IGNORE INTO Results (StudentID, Subject, Score, Term, TeacherID) VALUES (1, 'Math', 85, 'Term 1', 1)")
    cursor.execute("INSERT OR IGNORE INTO Results (StudentID, Subject, Score, Term, TeacherID) VALUES (1, 'English', 78, 'Term 1', 2)")
    cursor.execute("INSERT OR IGNORE INTO Results (StudentID, Subject, Score, Term, TeacherID) VALUES (2, 'Math', 92, 'Term 1', 1)")
    cursor.execute("INSERT OR IGNORE INTO Results (StudentID, Subject, Score, Term, TeacherID) VALUES (2, 'English', 88, 'Term 1', 3)")

    conn.commit()
    conn.close()

# Helper function to generate styled HTML with background
def get_html(content):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>KAFUMBWE GRADE BOOK SYSTEM</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%);
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 900px;
                margin: auto;
                background: rgba(255, 255, 255, 0.9);
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            }}
            h1 {{
                text-align: center;
                margin-bottom: 30px;
                color: #333;
                font-family: 'Arial Rounded MT Bold', cursive;
            }}
            a {{
                display: inline-block;
                margin-top: 15px;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: #fff;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }}
            a:hover {{
                background-color: #45a049;
            }}
            form {{
                background: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            label {{
                display: block;
                margin-top: 15px;
                font-weight: 600;
                color: #555;
            }}
            input[type=text], input[type=password], select, input[type=number] {{
                width: 100%; box-sizing: border-box;    // Ensure padding doesn't affect width
                padding: 18px 15px;
                margin-top: 20px;
                border: 2px solid #ccc;
                border-radius: 6px;
                font-size: 1.1em;
                min-height: 30px;
                transition: border-color 0.2s;
            }}
            input[type=text]:focus, input[type=password]:focus, select:focus, input[type=number]:focus {{
                border-color: #4CAF50;
                outline: none;
            }}
            input[type=submit] {{
                margin-top: 20px;
                padding: 12px 25px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1.1em;
                transition: background-color 0.3s ease;
            }}
            input[type=submit]:hover {{
                background-color: #45a049;
            }}
            /* Styling table for results */
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 25px;
            }}
            th, td {{
                padding: 14px;
                border: 1px solid #ddd;
                text-align: center;
                border-radius: 4px;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: 600;
            }}
            /* Buttons inside results table (if any) */
            .btn {{
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9em;
                margin: 2px;
            }}
            .edit-btn {{
                background-color: #2196F3;
                color: white;
            }}
            .delete-btn {{
                background-color: #f44336;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>KAFUMBWE GRADE BOOK SYSTEM</h1>
            {content}
        </div>
    </body>
    </html>
    """

# Basic server handler
class GradeSystemHandler(http.server.BaseHTTPRequestHandler):
    # Class variable to store current user session (UserID, Username, Role)
    user_session = {}
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)
        path = parsed_path.path

        if path == "/":
            self.show_home()
        elif path == "/login":
            self.show_login()
        elif path == "/dashboard":
            self.show_dashboard()
        elif path == "/view_results":
            self.view_results(params)
        elif path == "/teacher":
            self.show_teacher_page(params)
        elif path == "/show_recent_results":
            self.show_recent_results(params)
        elif path == "/teacher/edit_student":
            self.show_edit_student(params)
        elif path == "/logout":
            self.user_session = {}
            self.show_login()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = urllib.parse.parse_qs(self.rfile.read(length).decode())

        path = self.path

        if path == "/login":
            self.handle_login(data)
        elif path == "/teacher/add_results":
            self.process_add_results(data)
        elif path.startswith("/teacher/edit_result"):
            self.edit_result(data, path)
        elif path == "/teacher/delete_result":
            self.delete_result(data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")

    def show_home(self):
        html = get_html("""
            <h2 style="text-align:center;">Welcome to Kafumbwe GradeBook System.</h2>
            <p style="text-align:center; margin-top:30px; font-size:18px;">
                <a href="/login" style="display:inline-block; padding:12px 30px; background-color:#4CAF50; color:#fff; text-decoration:none; border-radius:8px; font-weight:bold;">Teacher Login</a>
            </p>
        """)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def show_login(self):
        html = get_html("""
            <h2 style="text-align:center;">Welcome to Kafumbwe Grade Book.</h2>
            <h3 style="text-align:center;">Login</h3>
            <form method="post" action="/login">
                <label>Username:</label>
                <input type="text" name="username" required />
                <label>Password:</label>
                <input type="password" name="password" id="password" required />

                <div style="margin-top:10px; margin-bottom:12px;">
                    <label for="showPassword" style="display:inline-flex; align-items:center;">
                        <input type="checkbox" id="showPassword" onclick="togglePassword()" style="margin-right:8px;" />
                        Show Password
                    </label>
                </div>

                <input type="submit" value="Login" />

                <script>
                    function togglePassword() {
                        var p = document.getElementById('password');
                        if (p.type === 'password') {
                            p.type = 'text';
                        } else {
                            p.type = 'password';
                        }
                    }
                </script>
            </form>
        """)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def handle_login(self, data):
        username = data.get("username", [""])[0]
        password = data.get("password", [""])[0]
        conn = sqlite3.connect("gradesystem.db")
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Role FROM Teachers WHERE Username=? AND Password=?", (username, password))
        row = cursor.fetchone()
        conn.close()
        if row:
            user_id, role = row[0], row[1]
            # Store user session
            GradeSystemHandler.user_session = {"user_id": user_id, "username": username, "role": role}
            if role == "teacher":
                self.send_response(302)
                self.send_header("Location", "/dashboard")
                self.end_headers()
            elif role == "pupil":
                self.send_response(302)
                self.send_header("Location", "/view_results")
                self.end_headers()
        else:
            self.show_login()

    def show_dashboard(self):
        # Fetch Statistics
        conn = sqlite3.connect("gradesystem.db")
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM Student")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Class")
        total_classes = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(Score) FROM Results")
        avg_score = cursor.fetchone()[0]
        avg_score = round(avg_score, 2) if avg_score else 0
        
        # Get average by subject
        cursor.execute("""
            SELECT Subject, AVG(Score) as avg_score 
            FROM Results 
            GROUP BY Subject 
            ORDER BY avg_score DESC
        """)
        subject_stats = cursor.fetchall()
        
        # Get top performers
        cursor.execute("""
            SELECT s.Name, AVG(r.Score) as avg_score
            FROM Student s
            JOIN Results r ON s.StudentID = r.StudentID
            GROUP BY s.StudentID
            ORDER BY avg_score DESC
            LIMIT 5
        """)
        top_performers = cursor.fetchall()
        
        # Get students needing help (avg < 70)
        cursor.execute("""
            SELECT s.Name, AVG(r.Score) as avg_score
            FROM Student s
            JOIN Results r ON s.StudentID = r.StudentID
            GROUP BY s.StudentID
            HAVING AVG(r.Score) < 70
            ORDER BY avg_score ASC
        """)
        at_risk_students = cursor.fetchall()
        

        
        # Get students by class
        cursor.execute("""
            SELECT c.ClassName, COUNT(s.StudentID) as count
            FROM Class c
            LEFT JOIN Student s ON c.ClassID = s.ClassID
            GROUP BY c.ClassID
            ORDER BY c.ClassName
        """)
        students_by_class = cursor.fetchall()
        
        conn.close()
        
        # Build subject stats HTML
        subject_stats_html = ""
        for subject, score in subject_stats:
            subject_stats_html += f"<tr><td>{subject}</td><td>{round(score, 2)}</td></tr>"
        
        # Build top performers HTML
        top_performers_html = ""
        for i, (name, score) in enumerate(top_performers, 1):
            top_performers_html += f"<tr><td>{i}</td><td>{name}</td><td>{round(score, 2)}%</td></tr>"
        
        # Build at-risk students HTML
        at_risk_html = ""
        if at_risk_students:
            for name, score in at_risk_students:
                at_risk_html += f"<tr><td>{name}</td><td>{round(score, 2)}%</td></tr>"
        else:
            at_risk_html = "<tr><td colspan='2'>No students below 70%</td></tr>"
        

        
        # Build students by class HTML
        students_class_html = ""
        for classname, count in students_by_class:
            students_class_html += f"<tr><td>{classname}</td><td>{count}</td></tr>"
        
        # Full dashboard HTML
        html_content = f"""
            <h2>Teacher's Dashboard</h2>
            <a href="/teacher" style="display:inline-block; padding:10px 20px; background-color:#2196F3; color:#fff; text-decoration:none; border-radius:5px; margin-bottom:20px;">Add Results</a>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-top:20px; margin-bottom:30px;">
                <div style="background:#e3f2fd; padding:20px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                    <h3 style="margin:0; color:#1976d2;">Total Students</h3>
                    <p style="font-size:2em; font-weight:bold; color:#1976d2; margin:10px 0 0 0;">{total_students}</p>
                </div>
                <div style="background:#f3e5f5; padding:20px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                    <h3 style="margin:0; color:#7b1fa2;">Total Classes</h3>
                    <p style="font-size:2em; font-weight:bold; color:#7b1fa2; margin:10px 0 0 0;">{total_classes}</p>
                </div>
                <div style="background:#e8f5e9; padding:20px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                    <h3 style="margin:0; color:#388e3c;">Average Score</h3>
                    <p style="font-size:2em; font-weight:bold; color:#388e3c; margin:10px 0 0 0;">{avg_score}%</p>
                </div>
                <div style="background:#fff3e0; padding:20px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                    <h3 style="margin:0; color:#f57c00;">At Risk Students</h3>
                    <p style="font-size:2em; font-weight:bold; color:#f57c00; margin:10px 0 0 0;">{len(at_risk_students)}</p>
                </div>
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:30px;">
                <div>
                    <h3 style="border-bottom:3px solid #4CAF50; padding-bottom:10px;">Top Performers</h3>
                    <table style="width:100%; border-collapse:collapse;">
                        <tr style="background-color:#f2f2f2;">
                            <th style="padding:10px; text-align:left; border:1px solid #ddd;">#</th>
                            <th style="padding:10px; text-align:left; border:1px solid #ddd;">Student Name</th>
                            <th style="padding:10px; text-align:center; border:1px solid #ddd;">Avg Score</th>
                        </tr>
                        {top_performers_html if top_performers_html else "<tr><td colspan='3' style='padding:10px; text-align:center; border:1px solid #ddd;'>No data available</td></tr>"}
                    </table>
                </div>
                
                <div>
                    <h3 style="border-bottom:3px solid #f44336; padding-bottom:10px;">Students Needing Help</h3>
                    <table style="width:100%; border-collapse:collapse;">
                        <tr style="background-color:#f2f2f2;">
                            <th style="padding:10px; text-align:left; border:1px solid #ddd;">Student Name</th>
                            <th style="padding:10px; text-align:center; border:1px solid #ddd;">Avg Score</th>
                        </tr>
                        {at_risk_html}
                    </table>
                </div>
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:30px;">
                <div>
                    <h3 style="border-bottom:3px solid #2196F3; padding-bottom:10px;">Subject Performance</h3>
                    <table style="width:100%; border-collapse:collapse;">
                        <tr style="background-color:#f2f2f2;">
                            <th style="padding:10px; text-align:left; border:1px solid #ddd;">Subject</th>
                            <th style="padding:10px; text-align:center; border:1px solid #ddd;">Avg Score</th>
                        </tr>
                        {subject_stats_html if subject_stats_html else "<tr><td colspan='2' style='padding:10px; text-align:center; border:1px solid #ddd;'>No data available</td></tr>"}
                    </table>
                </div>
                
                <div>
                    <h3 style="border-bottom:3px solid #ff9800; padding-bottom:10px;">Students by Class</h3>
                    <table style="width:100%; border-collapse:collapse;">
                        <tr style="background-color:#f2f2f2;">
                            <th style="padding:10px; text-align:left; border:1px solid #ddd;">Class Name</th>
                            <th style="padding:10px; text-align:center; border:1px solid #ddd;">Count</th>
                        </tr>
                        {students_class_html if students_class_html else "<tr><td colspan='2' style='padding:10px; text-align:center; border:1px solid #ddd;'>No data available</td></tr>"}
                    </table>
                </div>
            </div>
            
            <br/><a href="/logout" style="display:inline-block; margin-top:20px; padding:10px 20px; background-color:#f44336; color:#fff; text-decoration:none; border-radius:5px;">Logout</a>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(get_html(html_content).encode())

    def show_teacher_page(self, params):
        # Extract class options
        conn = sqlite3.connect("gradesystem.db")
        classes = conn.execute("SELECT ClassID, ClassName FROM Class").fetchall()
        conn.close()
        options = "".join([f'<option value="{c[0]}">{c[1]}</option>' for c in classes])

        html_content = f"""
            <h2>Teacher's Dashboard</h2>
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <a href="/dashboard" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px;">View Dashboard</a>
                <a href="/show_recent_results" style="padding: 10px 20px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 4px;">Show Recent Saved Results</a>
            </div>
            <h3 style="margin-top:30px;">Add Results for Student</h3>
            <form method="post" action="/teacher/add_results">
                <label>Exam Number:</label>
                <input type="text" name="exam_number" required />

                <label>Name:</label>
                <input type="text" name="name" required />

                <label>Class:</label>
                <select name="class_id" required>
                    {options}
                </select>

                <label style="margin-top:12px;">Term:</label>
                <select name="term" required>
                    <option value="Term 1">Term 1</option>
                    <option value="Term 2">Term 2</option>
                    <option value="Term 3">Term 3</option>
                </select>

                <h4 style="margin-top:20px;">Add Results:</h4>
                <div id="results-container" style="margin-top:15px;">
                    <div class="result-entry" style="margin-bottom:10px;">
                        <input type="text" name="subject[]" placeholder="Subject" required style="width:45%; margin-right:10px; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                        <input type="number" name="score[]" placeholder="Score" min="0" max="100" required style="width:20%; margin-right:10px; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                        <button type="button" onclick="this.parentElement.remove()" style="background:#f44336; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer;">Remove</button>
                        <button type="button" onclick="alert('Update logic goes here')" style="background:#2196F3; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer; margin-left:6px;">Update</button>
                    </div>
                </div>
                <button type="button" onclick="addResult()" style="margin-top:10px; padding:8px 16px; border:none; border-radius:4px; background:#2196F3; color:#fff; cursor:pointer;">Add Another Result</button>
                <br/><br/>
                <input type="submit" value="Save Results" style="background:#4CAF50; padding:10px 20px; border:none; border-radius:4px; color:#fff; font-size:1em; cursor:pointer;"/>
            </form>
            <script>
                function addResult() {{
                    const container = document.getElementById('results-container');
                    const div = document.createElement('div');
                    div.className = 'result-entry';
                    div.style.marginBottom = '10px';
                    div.innerHTML = `
                        <input type="text" name="subject[]" placeholder="Subject" required style="width:45%; margin-right:10px; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                        <input type="number" name="score[]" placeholder="Score" min="0" max="100" required style="width:20%; margin-right:10px; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                        <button type="button" onclick="this.parentElement.remove()" style="background:#f44336; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer;">Remove</button>
                        <button type="button" onclick="alert('Update logic goes here')" style="background:#2196F3; color:#fff; border:none; padding:8px 12px; border-radius:4px; cursor:pointer; margin-left:6px;">Update</button>
                    `;
                    container.appendChild(div);
                }}
            </script>
            <br/><a href="/logout" style="display:inline-block; margin-top:20px; padding:10px 20px; background-color:#f44336; color:#fff; text-decoration:none; border-radius:5px;">Logout</a>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(get_html(html_content).encode())

    def show_recent_results(self, params):
        # Provide an option to filter recent results by pupil
        conn = sqlite3.connect("gradesystem.db")
        cursor = conn.cursor()

        # Fetch students for selector
        cursor.execute("SELECT StudentID, Name, ExamNumber FROM Student ORDER BY Name")
        students = cursor.fetchall()

        # Determine if a specific student is requested
        student_id = None
        if params and "student_id" in params and params["student_id"]:
            try:
                student_id = int(params["student_id"][0])
            except Exception:
                student_id = None

        results_html = ""
        header_html = ""

        if student_id:
            # Get results only for the selected student
            cursor.execute("SELECT Name, ExamNumber FROM Student WHERE StudentID = ?", (student_id,))
            srow = cursor.fetchone()
            if srow:
                sel_name, sel_exam = srow
                header_html = f"<h3 style='margin-top:10px;'>Recent Results for <strong>{sel_name}</strong> ({sel_exam})</h3>"
            cursor.execute("""
                SELECT r.Subject, r.Score, r.Term, t.Username, c.ClassName
                FROM Results r
                LEFT JOIN Teachers t ON r.TeacherID = t.UserID
                LEFT JOIN Student s ON r.StudentID = s.StudentID
                LEFT JOIN Class c ON s.ClassID = c.ClassID
                WHERE r.StudentID = ?
                ORDER BY r.ResultID DESC
                LIMIT 50
            """, (student_id,))
            rows = cursor.fetchall()
            if rows:
                for subject, score, term, teacher, class_name in rows:
                    teacher_name = teacher if teacher else "Unknown"
                    results_html += f"<tr><td>{subject}</td><td>{score}</td><td>{term}</td><td>{class_name}</td><td>{teacher_name}</td></tr>"
            else:
                results_html = "<tr><td colspan='5' style='padding:10px; text-align:center; border:1px solid #ddd;'>No results for this pupil yet.</td></tr>"
            table_headers = "<th style='padding:12px; text-align:left; border:1px solid #ddd; font-weight:600;'>Subject</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Score</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Term</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Class</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Submitted By</th>"
        else:
            # Show recent results across all pupils
            cursor.execute("""
                SELECT s.StudentID, s.Name, s.ExamNumber, r.Subject, r.Score, r.Term, t.Username, c.ClassName
                FROM Results r
                JOIN Student s ON r.StudentID = s.StudentID
                LEFT JOIN Class c ON s.ClassID = c.ClassID
                LEFT JOIN Teachers t ON r.TeacherID = t.UserID
                ORDER BY r.ResultID DESC
                LIMIT 50
            """)
            rows = cursor.fetchall()
            if rows:
                for sid, name, exam_number, subject, score, term, teacher, class_name in rows:
                    teacher_name = teacher if teacher else "Unknown"
                    # add a quick link to view this pupil's recent results
                    view_link = f"/show_recent_results?student_id={sid}"
                    results_html += f"<tr><td><a href='{view_link}' style='text-decoration:none;color:#1976d2;'>{name}</a></td><td style='text-align:center;'>{exam_number}</td><td>{subject}</td><td style='text-align:center;'>{score}</td><td style='text-align:center;'>{term}</td><td style='text-align:center;'>{class_name}</td><td style='text-align:center;'>{teacher_name}</td></tr>"
            else:
                results_html = "<tr><td colspan='7' style='padding:10px; text-align:center; border:1px solid #ddd;'>No results saved yet</td></tr>"
            table_headers = "<th style='padding:12px; text-align:left; border:1px solid #ddd; font-weight:600;'>Student Name</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Exam Number</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Subject</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Score</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Term</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Class</th><th style='padding:12px; text-align:center; border:1px solid #ddd; font-weight:600;'>Submitted By</th>"

        conn.close()

        # Build student selector
        options_html = "<option value=''>-- All Pupils --</option>"
        for sid, name, exam in students:
            sel = ""
            if student_id and sid == student_id:
                sel = " selected"
            options_html += f"<option value='{sid}'{sel}>{name} ({exam})</option>"

        # Build pupil cards (aligned like dashboard cards)
        students_cards_html = ""
        if students:
            students_cards_html += "<div style='display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-top:18px;'>"
            role = GradeSystemHandler.user_session.get('role') if GradeSystemHandler.user_session else None
            for sid, name, exam in students:
                # Use dashboard-like pastel cards with a clear CTA
                students_cards_html += (
                    "<div style='background:#e3f2fd; padding:14px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.06); text-align:left;'>"
                    f"<h4 style='margin:6px 0 8px 0; color:#1976d2;'>Check Results for {name}</h4>"
                    f"<p style='margin:0 0 10px 0; color:#555;'>Exam: {exam}</p>"
                    f"<a href='/show_recent_results?student_id={sid}' style='display:inline-block; padding:8px 12px; background:#2196F3; color:#fff; text-decoration:none; border-radius:6px; margin-right:8px;'>View</a>"
                    + (f"<a href='/teacher/edit_student?student_id={sid}' style='display:inline-block; padding:8px 12px; background:#ff9800; color:#fff; text-decoration:none; border-radius:6px;'>Edit</a>" if role == 'teacher' else "")
                    + "</div>"
                )
            students_cards_html += "</div>"

        html_content = f"""
            <h2>Recent Saved Results</h2>
            <div style='display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;'>
                <div>
                    <a href="/teacher" style="display:inline-block; padding:8px 14px; background-color:#2196F3; color:#fff; text-decoration:none; border-radius:4px;">Back to Teacher Dashboard</a>
                    <a href="/show_recent_results" style="display:inline-block; padding:8px 14px; margin-left:8px; background:#9e9e9e; color:#fff; text-decoration:none; border-radius:4px;">Show All</a>
                </div>
                <form method='get' action='/show_recent_results' style='margin-top:6px;'>
                    <label style='font-weight:600; margin-right:8px;'>Filter by Pupil:</label>
                    <select name='student_id' style='padding:8px 10px; border-radius:6px; border:1px solid #ccc;' onchange='this.form.submit()'>
                        {options_html}
                    </select>
                    <noscript><input type='submit' value='View' style='padding:8px 12px; margin-left:8px; background:#4CAF50; color:#fff; border:none; border-radius:6px; cursor:pointer;'/></noscript>
                </form>
            </div>
            {students_cards_html}
            {header_html}
            {'<div style="margin-top:18px;"><table style="width:100%; border-collapse:collapse; margin-top:10px;"><tr style="background-color:#f2f2f2;">' + table_headers + '</tr>' + results_html + '</table></div>' if student_id else ''}
            <br/><a href="/logout" style="display:inline-block; margin-top:20px; padding:10px 20px; background-color:#f44336; color:#fff; text-decoration:none; border-radius:5px;">Logout</a>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(get_html(html_content).encode())

    def process_add_results(self, data):
        exam_number = data.get("exam_number", [""])[0]
        name = data.get("name", [""])[0]
        class_id = data.get("class_id", [""])[0]
        term = data.get("term", ["Term 1"])[0]
        subjects = data.get("subject[]", [])
        scores = data.get("score[]", [])
        
        # Get logged-in teacher's ID
        teacher_id = GradeSystemHandler.user_session.get("user_id")
        if not teacher_id:
            self.show_login()
            return
        
        if len(subjects) != len(scores):
            # Could add error message here
            self.show_teacher_page({})
            return
        conn = sqlite3.connect("gradesystem.db")
        cursor = conn.cursor()
        # Check if student exists
        cursor.execute("SELECT StudentID FROM Student WHERE ExamNumber=?", (exam_number,))
        row = cursor.fetchone()
        if row:
            student_id = row[0]
        else:
            cursor.execute("INSERT INTO Student (ExamNumber, Name, ClassID) VALUES (?, ?, ?)", (exam_number, name, class_id))
            student_id = cursor.lastrowid
        # Insert results with TeacherID
        for subj, score in zip(subjects, scores):
            cursor.execute("INSERT INTO Results (StudentID, Subject, Score, Term, TeacherID) VALUES (?, ?, ?, ?, ?)",
                           (student_id, subj, int(score), term, teacher_id))
        conn.commit()
        conn.close()
        self.send_response(302)
        self.send_header("Location", "/teacher")
        self.end_headers()

    def show_edit_student(self, params):
        # Only teachers can edit
        role = GradeSystemHandler.user_session.get('role') if GradeSystemHandler.user_session else None
        if role != 'teacher':
            self.show_login()
            return

        student_id = None
        if params and 'student_id' in params:
            try:
                student_id = int(params['student_id'][0])
            except Exception:
                student_id = None

        if not student_id:
            # redirect back to recent results
            self.send_response(302)
            self.send_header('Location', '/show_recent_results')
            self.end_headers()
            return

        conn = sqlite3.connect('gradesystem.db')
        cursor = conn.cursor()
        cursor.execute('SELECT StudentID, Name, ExamNumber FROM Student WHERE StudentID=?', (student_id,))
        srow = cursor.fetchone()
        if not srow:
            conn.close()
            self.send_response(302)
            self.send_header('Location', '/show_recent_results')
            self.end_headers()
            return

        _, name, exam = srow
        # Fetch results for this student
        cursor.execute('''
            SELECT r.ResultID, r.Subject, r.Score, r.Term, t.Username
            FROM Results r
            LEFT JOIN Teachers t ON r.TeacherID = t.UserID
            WHERE r.StudentID = ?
            ORDER BY r.ResultID DESC
        ''', (student_id,))
        results = cursor.fetchall()
        conn.close()

        # Build editable form
        rows_html = ''
        if results:
            for rid, subj, score, term, teacher in results:
                teacher_name = teacher if teacher else 'Unknown'
                rows_html += f"<tr><td>{subj}</td><td><input type='number' name='score[]' value='{score}' min='0' max='100' style='width:80px; padding:6px; border-radius:4px; border:1px solid #ccc;' required/></td><td>{term}</td><td>{teacher_name}</td><td><input type='hidden' name='result_id[]' value='{rid}'/></td></tr>"
        else:
            rows_html = "<tr><td colspan='5' style='text-align:center; padding:10px;'>No results to edit for this pupil.</td></tr>"

        html_content = f"""
            <h2>Edit Results for {name} ({exam})</h2>
            <form method='post' action='/teacher/edit_result'>
                <input type='hidden' name='student_id' value='{student_id}'/>
                <table style='width:100%; border-collapse:collapse; margin-top:10px;'>
                    <tr style='background:#f2f2f2;'><th style='padding:10px; text-align:left;'>Subject</th><th style='padding:10px;'>Score</th><th style='padding:10px;'>Term</th><th style='padding:10px;'>Submitted By</th><th></th></tr>
                    {rows_html}
                </table>
                <div style='margin-top:16px;'>
                    <input type='submit' value='Save Corrections' style='padding:10px 16px; background:#4CAF50; color:#fff; border:none; border-radius:6px; cursor:pointer;'/>
                    <a href='/show_recent_results?student_id={student_id}' style='margin-left:12px; padding:10px 14px; background:#9e9e9e; color:#fff; text-decoration:none; border-radius:6px;'>Cancel</a>
                </div>
            </form>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(get_html(html_content).encode())

    def edit_result(self, data, path):
        # Only teachers can submit edits
        role = GradeSystemHandler.user_session.get('role') if GradeSystemHandler.user_session else None
        if role != 'teacher':
            self.show_login()
            return

        student_id = data.get('student_id', [None])[0]
        result_ids = data.get('result_id[]', [])
        scores = data.get('score[]', [])

        if not student_id or not result_ids or not scores or len(result_ids) != len(scores):
            # invalid submission
            self.send_response(302)
            self.send_header('Location', '/show_recent_results')
            self.end_headers()
            return

        conn = sqlite3.connect('gradesystem.db')
        cursor = conn.cursor()
        try:
            for rid, sc in zip(result_ids, scores):
                try:
                    cursor.execute('UPDATE Results SET Score = ? WHERE ResultID = ?', (int(sc), int(rid)))
                except Exception:
                    pass
            conn.commit()
        finally:
            conn.close()

        # Redirect back to the student's recent results view
        self.send_response(302)
        self.send_header('Location', f'/show_recent_results?student_id={student_id}')
        self.end_headers()

    def view_results(self, params):
        # Populate class options
        conn = sqlite3.connect("gradesystem.db")
        classes = conn.execute("SELECT ClassID, ClassName FROM Class").fetchall()
        
        # Get list of available exam numbers for reference
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ExamNumber FROM Student ORDER BY ExamNumber")
        available_exams = cursor.fetchall()
        conn.close()
        
        options = "".join([f'<option value="{c[0]}">{c[1]}</option>' for c in classes])
        
        exam_list = ""
        if available_exams:
            exam_list = "<p><strong>Available Exam Numbers:</strong> " + ", ".join([str(e[0]) for e in available_exams]) + "</p>"
        else:
            exam_list = "<p style='color:#ff6b6b;'><strong>No students registered yet. Please contact your teacher to get registered.</strong></p>"
        
        # Show form for students to enter exam number and class
        html = f"""
            <h2>View Your Results</h2>
            {exam_list}
            <form method="get" action="/view_results" style="margin-top:20px;">
                <label>Enter Exam Number:</label>
                <input type="text" name="exam_number" placeholder="e.g., EXAM001 or 170900600401" required style="width:100%; padding:8px; border-radius:4px; border:1px solid #ccc;"/>
                <label style="margin-top:15px;">Select Class:</label>
                <select name="class_id" required style="width:100%; padding:8px; border-radius:4px; border:1px solid #ccc;">
                    <option value="">-- Select your class --</option>
                    {options}
                </select>
                <br/><br/>
                <input type="submit" value="View Results" style="background:#4CAF50; padding:10px 20px; border:none; border-radius:4px; color:#fff; font-size:1em; cursor:pointer;"/>
            </form>
        """

        # If parameters provided, show results
        if "exam_number" in params and "class_id" in params:
            exam_number = params["exam_number"][0]
            class_id = params["class_id"][0]
            conn = sqlite3.connect("gradesystem.db")
            cursor = conn.cursor()
            cursor.execute("SELECT StudentID, Name FROM Student WHERE ExamNumber=? AND ClassID=?", (exam_number, class_id))
            row = cursor.fetchone()
            if row:
                student_id, name = row[0], row[1]
                # Get all results from all teachers for this student
                cursor.execute("""
                    SELECT r.Subject, r.Score, r.Term, t.Username, r.TeacherID
                    FROM Results r
                    LEFT JOIN Teachers t ON r.TeacherID = t.UserID
                    WHERE r.StudentID=?
                    ORDER BY r.Term, t.Username, r.Subject
                """, (student_id,))
                results = cursor.fetchall()
                if results:
                    avg_score = sum([r[1] for r in results]) / len(results)
                    table_html = f"<h3 style='margin-top:30px; color:#333;'>Your Results:</h3>"
                    table_html += f"<p><strong>Student Name: {name}</strong></p>"
                    table_html += f"<table><tr><th>Subject</th><th>Score</th><th>Term</th><th>Teacher</th></tr>"
                    for subj, score, term, teacher, _ in results:
                        teacher_name = teacher if teacher else "Unknown"
                        table_html += f"<tr><td>{subj}</td><td>{score}</td><td>{term}</td><td>{teacher_name}</td></tr>"
                    table_html += f"</table><p><strong>Average Score: {round(avg_score, 2)}%</strong></p>"
                else:
                    table_html = f"<h3 style='margin-top:30px; color:#333;'>Your Results:</h3>"
                    table_html += f"<p><strong>Student Name: {name}</strong></p>"
                    table_html += "<p style='color:#ff6b6b; font-size:1.1em; padding:20px; background:#ffe0e0; border-radius:8px; text-align:center;'><strong>Not Published Yet.</strong></p>"
            else:
                table_html = "<p style='color:#ff6b6b;'>Student not found. Please verify your exam number and class are correct.</p>"
            conn.close()
            html += table_html
            html += "<br/><a href='/' style='display:inline-block; padding:10px 20px; background-color:#4CAF50; color:#fff; text-decoration:none; border-radius:5px; margin-top:20px;'>Back to Home</a>"

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(get_html(html).encode())

# Initialize database and run server
def main():
    init_db()
    PORT = int(os.environ.get("PORT", "3003"))
    with socketserver.TCPServer(("", PORT), GradeSystemHandler) as server:
        print(f"Server running at http://localhost:{3003}")
        print("Open your browser and visit that URL.")
        server.serve_forever()

if __name__ == "__main__":
    main()