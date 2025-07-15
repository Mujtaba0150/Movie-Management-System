from flask import Flask, redirect, url_for, session, render_template, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from werkzeug.utils import secure_filename
import json
from mysql.connector import Error
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Limit to 5MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Hello123",
        database="db"
    )

def get_genres():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Genres")
        genres = cursor.fetchall()
        return genres
    except mysql.connector.Error as err:
        print("Error: ", err)
    finally:
        cursor.close()
        conn.close()

def get_actors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Actors")
        actors = cursor.fetchall()
        return actors
    except mysql.connector.Error as err:
        print("Error: ", err)
    finally:
        cursor.close()
        conn.close()

def get_languages():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT language FROM movies GROUP BY language")
        languages = cursor.fetchall()
        return languages
    except mysql.connector.Error as err:
        print("Error: ", err)
    finally:
        cursor.close()
        conn.close()

def get_movies(page=1):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Movies ORDER BY averageRating DESC LIMIT " + str((page-1)*10) + ", 10"
        cursor.execute(query)
        movies = cursor.fetchall()
        return movies
    except mysql.connector.Error as err:
        print("Error: ", err)
    finally:
        cursor.close()
        conn.close()

def get_number_of_pages():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM movierequests WHERE status = 'pending'")
        count = cursor.fetchone()
        return count['count']/10
    except mysql.connector.Error as err:
        print("Error: ", err)
    finally:
        cursor.close()
        conn.close()

def get_movierequest():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM movierequests WHERE status = 'pending'")
        movierequests = cursor.fetchall()
        return movierequests
    except mysql.connector.Error as err:
        print("Error: ", err)
    finally:
        cursor.close()
        conn.close()

@app.route('/updateRequest', methods=['POST'])
def updateRequest():
    requestId = request.form.get('requestId')
    title = request.form.get('title')
    description = request.form.get('description')
    releaseYear = request.form.get('releaseYear')
    language = request.form.get('language')
    directorName = request.form.get('directorName')
    genre = request.form.get('genre')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE movierequests
            SET title = %s, description = %s, releaseYear = %s, language = %s,
                directorName = %s, genreName = %s
            WHERE requestId = %s
        """, (title, description, releaseYear, language, directorName, genre, requestId))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('adminHome'))

@app.route('/approveRequest', methods=['POST'])
def approveRequest():
    try:
        requestId = request.form.get('requestId')
        selectedActorIds = request.form.get('selectedActorIds')
        newActors = request.form.get('newActors')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM movierequests
            WHERE requestId = %s
        """, (requestId,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Request not found"}), 404
        poster = request.files.get('poster')
        if not poster:
            return jsonify({"error": "Poster image is required."}), 400

        if not allowedFile(poster.filename):
            return jsonify({"error": "Invalid image file type."}), 400

        try:
            selectedActorIds = json.loads(selectedActorIds)
            newActors = json.loads(newActors)
        except Exception:
            return jsonify({"error": "Invalid actor data."}), 400

        originalExtension = os.path.splitext(poster.filename)[1]  # e.g. '.jpg', '.png', '.heic'

        # Sanitize the title to make it a safe filename
        safeTitle = secure_filename(result['title'])

        # Build final filename with original extension
        finalFilename = safeTitle + originalExtension

        # Save the file
        poster.save(os.path.join('static/img', finalFilename))

        # Check director exists
        cursor.execute("""
            SELECT * FROM Directors
            WHERE name = %s
        """, (result['directorName'],))
        director = cursor.fetchone()
        
        if not director:
            cursor.execute("""
                INSERT INTO Directors (name)
                VALUES (%s)
            """, (result['directorName'],))
            conn.commit()  # commit immediately if you want to use the new director later
        
        cursor.execute("""
            SELECT * FROM Directors
            WHERE name = %s
        """, (result['directorName'],))
        director = cursor.fetchone()
        
        # Check genre exists - FETCH before next execute!
        cursor.execute("""
            SELECT * FROM Genres
            WHERE name = %s
            LIMIT 1
        """, (result['genreName'],))
        genre = cursor.fetchone()
        
        if not genre:
            cursor.execute("""
                INSERT INTO genres (name)
                VALUES (%s)
            """, (result['genreName'],))
            conn.commit()

        # Now fetch the genre again to get its id
        cursor.execute("""
            SELECT * FROM genres
            WHERE name = %s
            LIMIT 1
        """, (result['genreName'],))
        genre = cursor.fetchone()

        # Insert new movie using genre id
        cursor.execute("""
            INSERT INTO Movies (title, description, releaseYear, language, genreId, DirectorId)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (result['title'], result['description'], result['releaseYear'], result['language'], genre['genreId'], director['directorId']))
        conn.commit()

        # Delete the request
        cursor.execute("""
            DELETE FROM movierequests
            WHERE requestId = %s
        """, (requestId,))
        conn.commit()

        # Get the movieId of the newly inserted movie
        cursor.execute("""
            SELECT movieId FROM Movies
            WHERE title = %s AND releaseYear = %s
            AND language = %s
            AND genreId = %s AND DirectorId = %s
        """, (result['title'], result['releaseYear'], result['language'], genre['genreId'], director['directorId']))
        movieId = cursor.fetchone()

        for actorId in selectedActorIds:
            cursor.execute("""
                INSERT INTO MovieActors (movieId, actorId)
                VALUES (%s, %s)
            """, (movieId['movieId'], actorId))

        # Insert new actors
        for actor in newActors:
            print(actor)
            cursor.execute("""
                INSERT INTO Actors (name)
                VALUES (%s)
            """, (actor,))
            conn.commit()
            cursor.execute("""
                SELECT actorId FROM Actors
                WHERE name = %s
            """, (actor,))
            newActorId = cursor.fetchone()
            print(f"New Actor ID: {newActorId}")
            print(f"Movie ID: {movieId}")
            
            try :
                cursor.execute("""
                INSERT INTO MovieActors (movieId, actorId)
                VALUES (%s, %s)
            """, (movieId['movieId'], newActorId['actorId']))
                conn.commit()
            except Error as e:
                print(f"MySQL Error: {e}")

        return jsonify({"message": "Request accepted successfully!"}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        cursor.close()
        conn.close()

        
@app.route('/rejectRequest', methods=['POST'])
def rejectRequest():
    data = request.get_json()
    requestId = data.get('requestId')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            UPDATE movierequests
            SET status = 'rejected'
            WHERE requestId = %s
        """, (requestId,))
        conn.commit()
        return jsonify(success=True), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['email']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Check if user exists by username or email
            cursor.execute("""
            SELECT * FROM Users 
            WHERE (username = %s OR email = %s)
            AND role = 'admin'
            """, (identifier, identifier))

            user = cursor.fetchone()

            if not user:
                return render_template('adminSignIn.html', error="Username or email does not exist")

            # Validate password
            if not check_password_hash(user['passwordHash'], password):
                return render_template('adminSignIn.html', error="Password is incorrect")
            
            # Set session (optional)
            session['userId'] = user['userId']
            session['username'] = user['username']
            session['role'] = user['role']

            return redirect(url_for('adminHome'))  # Redirect to adminHome/dashboard

        except mysql.connector.Error as err:
            return render_template('adminSignIn.html', error="Database error: " + str(err))

        finally:
            cursor.close()
            conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashedPassword = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Users WHERE email = %s AND role = 'admin'", (email,))
            if cursor.fetchone():
                return render_template('adminSignUp.html', error="Email already exists.")
            cursor.execute("SELECT * FROM Users WHERE username = %s AND role = 'admin'", (username,))
            if cursor.fetchone():
                return render_template('adminSignUp.html', error="Username already exists.")

            cursor.execute("""
                INSERT INTO Users (username, email, passwordHash, role)
                VALUES (%s, %s, %s, 'admin')
            """, (username, email, hashedPassword))

            conn.commit()
            return redirect(url_for('adminSignIn'))

        except mysql.connector.Error as err:
            flash("Database error: " + str(err))
            return redirect(url_for('adminSignUp'))

        finally:
            cursor.close()
            conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('userId', None)
    session.clear()
    return redirect(url_for('adminHome'))
