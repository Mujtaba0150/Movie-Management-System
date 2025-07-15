from flask import Flask, redirect, url_for, session, render_template, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)

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

def get_directors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Directors")
        directors = cursor.fetchall()
        return directors
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
        for movie in movies:
            cursor.execute("SELECT name FROM Genres WHERE genreId = %s", (movie['genreId'],))
            movie['genreName'] = cursor.fetchone()['name']
        return movies
    except mysql.connector.Error as err:
        print("Error: ", err)
    finally:
        imageFolder = os.path.join(app.static_folder, 'img')
        for movie in movies:
            for ext in ['.jpg', '.png', '.heic']:
                possiblePath = os.path.join(imageFolder, movie['title'] + ext)
                if os.path.exists(possiblePath):
                    movie['imageFilename'] = 'img/' + movie['title'] + ext
                    break
        cursor.close()
        conn.close()

def get_number_of_pages():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM Movies")
        count = cursor.fetchone()
        return count['count']/10
    except mysql.connector.Error as err:
        print("Error: ", err)
    finally:
        cursor.close()
        conn.close()

def get_request_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Total requests
    cursor.execute("SELECT COUNT(*) as total_requests FROM MovieRequests")
    total_requests = cursor.fetchone()['total_requests']
    
    # Requests by status
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM MovieRequests 
        GROUP BY status
    """)
    requests_by_status = cursor.fetchall()
    
    # Recent requests
    cursor.execute("""
        SELECT title, status, submittedAt 
        FROM MovieRequests 
        ORDER BY submittedAt DESC 
        LIMIT 5
    """)
    recent_requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        'total_requests': total_requests,
        'requests_by_status': requests_by_status,
        'recent_requests': recent_requests
    }

def get_user_activity():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Total users
    cursor.execute("SELECT COUNT(*) as total_users FROM Users")
    total_users = cursor.fetchone()['total_users']
    
    # Recent signups
    cursor.execute("""
        SELECT username, createdAt 
        FROM Users 
        ORDER BY createdAt DESC 
        LIMIT 5
    """)
    recent_users = cursor.fetchall()
    
    # Watchlist stats
    cursor.execute("SELECT COUNT(*) as total_watchlists FROM Watchlists")
    total_watchlists = cursor.fetchone()['total_watchlists']
    
    cursor.execute("""
        SELECT w.name, COUNT(wm.movieId) as movie_count 
        FROM Watchlists w
        LEFT JOIN WatchlistMovies wm ON w.watchlistId = wm.watchlistId
        GROUP BY w.watchlistId
        ORDER BY movie_count DESC
        LIMIT 5
    """)
    popular_watchlists = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        'total_users': total_users,
        'recent_users': recent_users,
        'total_watchlists': total_watchlists,
        'popular_watchlists': popular_watchlists
    }

def get_genres_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Movies count by genre
    cursor.execute("""
        SELECT g.name, COUNT(m.movieId) as movie_count 
        FROM Genres g
        LEFT JOIN Movies m ON g.genreId = m.genreId
        GROUP BY g.genreId
        ORDER BY movie_count DESC
    """)
    genres_stats = cursor.fetchall()
    
    # Average rating by genre
    cursor.execute("""
        SELECT g.name, AVG(m.averageRating) as avg_rating 
        FROM Genres g
        JOIN Movies m ON g.genreId = m.genreId
        WHERE m.numberOfRatings > 0
        GROUP BY g.genreId
        ORDER BY avg_rating DESC
    """)
    genres_ratings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        'genres_stats': genres_stats,
        'genres_ratings': genres_ratings
    }

def get_genres_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Movies count by genre
    cursor.execute("""
        SELECT g.name, COUNT(m.movieId) as movie_count 
        FROM Genres g
        LEFT JOIN Movies m ON g.genreId = m.genreId
        GROUP BY g.genreId
        ORDER BY movie_count DESC
    """)
    genres_stats = cursor.fetchall()
    
    # Average rating by genre
    cursor.execute("""
        SELECT g.name, AVG(m.averageRating) as avg_rating 
        FROM Genres g
        JOIN Movies m ON g.genreId = m.genreId
        WHERE m.numberOfRatings > 0
        GROUP BY g.genreId
        ORDER BY avg_rating DESC
    """)
    genres_ratings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        'genres_stats': genres_stats,
        'genres_ratings': genres_ratings
    }

def get_movies_overview():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Total movies count
    cursor.execute("SELECT COUNT(*) as total_movies FROM Movies")
    total_movies = cursor.fetchone()['total_movies']
    
    # Average rating across all movies
    cursor.execute("SELECT AVG(averageRating) as avg_rating FROM Movies WHERE numberOfRatings > 0")
    avg_rating = round(cursor.fetchone()['avg_rating'], 2)
    
    # Movies by year
    cursor.execute("""
        SELECT releaseYear, COUNT(*) as count 
        FROM Movies 
        GROUP BY releaseYear 
        ORDER BY releaseYear DESC
        LIMIT 10
    """)
    movies_by_year = cursor.fetchall()
    
    # Top rated movies
    cursor.execute("""
        SELECT title, averageRating 
        FROM Movies 
        ORDER BY averageRating DESC 
        LIMIT 5
    """)
    top_rated = cursor.fetchall()
    
    # Most reviewed movies
    cursor.execute("""
        SELECT m.title, COUNT(r.id) as review_count 
        FROM Movies m
        LEFT JOIN Reviews r ON m.movieId = r.movieId
        GROUP BY m.movieId
        ORDER BY review_count DESC
        LIMIT 5
    """)
    most_reviewed = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        'total_movies': total_movies,
        'avg_rating': avg_rating,
        'movies_by_year': movies_by_year,
        'top_rated': top_rated,
        'most_reviewed': most_reviewed
    }

def create_tables():
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Creating tables in order to satisfy FK constraints
    createUsersTable = """
    CREATE TABLE IF NOT EXISTS users (
        userId int NOT NULL AUTO_INCREMENT,
        username varchar(50) NOT NULL,
        email varchar(100) NOT NULL,
        passwordHash varchar(255) NOT NULL,
        role enum('user','admin') DEFAULT 'user',
        createdAt timestamp NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (userId)
    )
    """

    createDirectorsTable = """
    CREATE TABLE IF NOT EXISTS directors (
        directorId int NOT NULL AUTO_INCREMENT,
        name varchar(100) NOT NULL,
        PRIMARY KEY (directorId)
    )
    """

    createGenresTable = """
    CREATE TABLE IF NOT EXISTS genres (
        genreId int NOT NULL AUTO_INCREMENT,
        name varchar(50) NOT NULL,
        PRIMARY KEY (genreId),
        UNIQUE KEY name (name)
    )
    """

    createMoviesTable = """
    CREATE TABLE IF NOT EXISTS movies (
        movieId int NOT NULL AUTO_INCREMENT,
        title varchar(255) NOT NULL,
        description text,
        releaseYear year DEFAULT NULL,
        language varchar(50) DEFAULT NULL,
        directorId int DEFAULT NULL,
        genreId int DEFAULT NULL,
        averageRating decimal(3,2) GENERATED ALWAYS AS ((totalRating / NULLIF(numberOfRatings,0))) STORED,
        totalRating int DEFAULT 0,
        numberOfRatings int DEFAULT 0,
        createdAt timestamp NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (movieId),
        KEY directorId (directorId),
        KEY genreId (genreId),
        CONSTRAINT movies_ibfk_1 FOREIGN KEY (directorId) REFERENCES directors (directorId),
        CONSTRAINT movies_ibfk_2 FOREIGN KEY (genreId) REFERENCES genres (genreId)
    )
    """

    createActorsTable = """
    CREATE TABLE IF NOT EXISTS actors (
        actorId int NOT NULL AUTO_INCREMENT,
        name varchar(100) NOT NULL,
        PRIMARY KEY (actorId)
    )
    """

    createMovieActorsTable = """
    CREATE TABLE IF NOT EXISTS movieactors (
        movieId int NOT NULL,
        actorId int NOT NULL,
        PRIMARY KEY (movieId, actorId),
        KEY actorId (actorId),
        CONSTRAINT movieactors_ibfk_1 FOREIGN KEY (movieId) REFERENCES movies (movieId) ON DELETE CASCADE,
        CONSTRAINT movieactors_ibfk_2 FOREIGN KEY (actorId) REFERENCES actors (actorId) ON DELETE CASCADE
    )
    """

    createMovieRequestsTable = """
    CREATE TABLE IF NOT EXISTS movierequests (
        requestId int NOT NULL AUTO_INCREMENT,
        userId int DEFAULT NULL,
        title varchar(255) NOT NULL,
        description text,
        releaseYear year DEFAULT NULL,
        language varchar(50) DEFAULT NULL,
        directorName varchar(100) DEFAULT NULL,
        genreName varchar(50) DEFAULT NULL,
        status enum('pending','approved','rejected') DEFAULT 'pending',
        submittedAt timestamp NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (requestId),
        KEY userId (userId),
        CONSTRAINT movierequests_ibfk_1 FOREIGN KEY (userId) REFERENCES users (userId) ON DELETE SET NULL
    )
    """

    createWatchlistsTable = """
    CREATE TABLE IF NOT EXISTS watchlists (
        watchlistId int NOT NULL AUTO_INCREMENT,
        userId int DEFAULT NULL,
        name varchar(100) NOT NULL,
        createdAt timestamp NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (watchlistId),
        KEY userId (userId),
        CONSTRAINT watchlists_ibfk_1 FOREIGN KEY (userId) REFERENCES users (userId) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    createWatchlistMoviesTable = """
    CREATE TABLE IF NOT EXISTS watchlistmovies (
        watchlistId int NOT NULL,
        movieId int NOT NULL,
        PRIMARY KEY (watchlistId, movieId),
        KEY movieId (movieId),
        CONSTRAINT watchlistmovies_ibfk_1 FOREIGN KEY (watchlistId) REFERENCES watchlists (watchlistId) ON DELETE CASCADE,
        CONSTRAINT watchlistmovies_ibfk_2 FOREIGN KEY (movieId) REFERENCES movies (movieId) ON DELETE CASCADE
    )
    """

    createReviewsTable = """
    CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userId INT NOT NULL,
    movieId INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userId) REFERENCES users(userId),
    FOREIGN KEY (movieId) REFERENCES movies(movieId)
    )
    """

    statements = [
        createUsersTable,
        createDirectorsTable,
        createGenresTable,
        createMoviesTable,
        createActorsTable,
        createMovieActorsTable,
        createMovieRequestsTable,
        createReviewsTable,
        createWatchlistsTable,
        createWatchlistMoviesTable,
        createReviewsTable,
    ]

    for statement in statements:
        cursor.execute(statement)

    conn.commit()
    cursor.close()


@app.route('/getPage', methods=['GET'])
def getPage():
    page = request.args.get('page')
    if page is None:
        page = 1
    
    page = int(page)
    return render_template('movies.html', page=page, totalPages=get_number_of_pages(), genres=get_genres(), actors=get_actors(), movies=get_movies(page))



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

            cursor.execute("SELECT * FROM Users WHERE email = %s AND role = 'user'", (email,))
            if cursor.fetchone():
                return render_template('signUp.html', error="Email already exists.")
            cursor.execute("SELECT * FROM Users WHERE username = %s AND role = 'user'", (username,))
            if cursor.fetchone():
                return render_template('signUp.html', error="Username already exists.")

            cursor.execute("""
                INSERT INTO Users (username, email, passwordHash, role)
                VALUES (%s, %s, %s, 'user')
            """, (username, email, hashedPassword))

            conn.commit()
            return redirect(url_for('signIn'))

        except mysql.connector.Error as err:
            flash("Database error: " + str(err))
            return redirect(url_for('signUp'))

        finally:
            cursor.close()
            conn.close()

@app.route('/login', methods=['GET', 'POST'])
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
            AND role = 'user'
            """, (identifier, identifier))

            user = cursor.fetchone()

            if not user:
                return render_template('signIn.html', error="Username or email does not exist")

            # Validate password
            if not check_password_hash(user['passwordHash'], password):
                return render_template('signIn.html', error="Password is incorrect")
            
            # Set session (optional)
            session['userId'] = user['userId']
            session['username'] = user['username']
            session['role'] = user['role']

            return redirect(url_for('movies'))

        except mysql.connector.Error as err:
            return render_template('signIn.html', error="Database error: " + str(err))

        finally:
            cursor.close()
            conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('userId', None)
    session.clear()
    return redirect(url_for('home'))

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').strip()
    genreIds = request.form.getlist('genres')
    actorIds = request.form.getlist('actors')
    languages = request.form.getlist('languages')
    ratingMax = request.form.get('ratingMax')

    if not query and not genreIds and not actorIds and not languages and not ratingMax:
        print("Error: Empty search query and filters")
        return redirect(url_for('movies'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT DISTINCT M.*, G.name AS genreName
        FROM Movies M
        LEFT JOIN MovieActors MA ON M.movieId = MA.movieId
        INNER JOIN Genres G ON M.genreId = G.genreId
        WHERE 1 = 1
    """
    params = []

    if query:
        sql += " AND M.title LIKE %s"
        params.append(f"%{query}%")
    if genreIds:
        sql += " AND M.genreId IN (" + ",".join(["%s"] * len(genreIds)) + ")"
        params.extend(genreIds)
    if actorIds:
        sql += " AND MA.actorId IN (" + ",".join(["%s"] * len(actorIds)) + ")"
        params.extend(actorIds)
    if languages:
        sql += " AND M.language IN (" + ",".join(["%s"] * len(languages)) + ")"
        params.extend(languages)
    if int(ratingMax) > 0:
        sql += " AND M.averageRating <= %s"
        params.append(ratingMax)
    if int(ratingMax) == 0:
        sql += " AND M.averageRating IS NULL"
    cursor.execute(sql, params)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'movies.html',
        page=1,
        totalPages=get_number_of_pages(),
        genres=get_genres(),
        actors=get_actors(),
        languages=get_languages(),
        movies=results)



@app.route('/get_user_watchlists')
def getUserWatchlists():
    if 'userId' not in session:
        return jsonify({'watchlists': []})

    userId = session['userId']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT watchlistId, name FROM Watchlists WHERE userId = %s", (userId,))
    watchlists = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({'watchlists': watchlists})

@app.route('/add_to_watchlist', methods=['POST'])
def addToWatchlist():
    if 'userId' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'})

    data = request.get_json()
    movieId = data.get('movieId')
    watchlistId = data.get('watchlistId')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already exists
    cursor.execute("SELECT * FROM WatchlistMovies WHERE movieId = %s AND watchlistId = %s", (movieId, watchlistId))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'error': 'Movie already in watchlist'})

    cursor.execute("INSERT INTO WatchlistMovies (watchlistId, movieId) VALUES (%s, %s)", (watchlistId, movieId))
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({'success': True})

@app.route('/create_watchlist_and_add', methods=['POST'])
def createWatchlistAndAdd():
    if 'userId' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'})

    data = request.get_json()
    name = data.get('name')
    movieId = data.get('movieId')
    userId = session['userId']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if a watchlist with the same name already exists for this user
    cursor.execute("SELECT watchlistId FROM Watchlists WHERE userId = %s AND name = %s", (userId, name))
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'error': 'Watchlist already exists'})

    # Create the new watchlist
    cursor.execute("INSERT INTO Watchlists (userId, name) VALUES (%s, %s)", (userId, name))
    newWatchlistId = cursor.lastrowid

    # Add the movie to the new watchlist
    cursor.execute("INSERT INTO WatchlistMovies (watchlistId, movieId) VALUES (%s, %s)", (newWatchlistId, movieId))
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({'success': True})

@app.route('/renameWatchlist/<int:watchlistId>', methods=['POST'])
def renameWatchlist(watchlistId):
    data = request.get_json()
    newName = data.get('newName', '').strip()
    userId = session.get('userId')

    if not newName or not userId:
        return 'Invalid request', 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Watchlists SET name = %s WHERE watchlistId = %s AND userId = %s", (newName, watchlistId, userId))
    conn.commit()
    return 'Watchlist renamed', 200


@app.route('/deleteWatchlist/<int:watchlistId>', methods=['POST'])
def deleteWatchlist(watchlistId):
    userId = session.get('userId')
    if not userId:
        return 'Unauthorized', 401

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM WatchlistMovies WHERE watchlistId = %s", (watchlistId,))
    cursor.execute("DELETE FROM Watchlists WHERE watchlistId = %s AND userId = %s", (watchlistId, userId))
    conn.commit()
    return 'Watchlist deleted', 200


@app.route('/removeMovieFromWatchlist', methods=['POST'])
def removeMovieFromWatchlist():
    data = request.get_json()
    movieId = data.get('movieId')
    watchlistId = data.get('watchlistId')

    if not movieId or not watchlistId:
        return jsonify({'error': 'Missing data'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM WatchlistMovies WHERE watchlistId = %s AND movieId = %s", (watchlistId, movieId))
        conn.commit()
        
        cursor.close()
        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"Error removing movie from watchlist: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    
@app.route('/rateMovie', methods=['POST'])
def rateMovie():
    data = request.get_json()
    movieId = data.get('movieId')
    rating = data.get('rating')

    if not movieId or not rating:
        return "Missing data", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user has already rated this movie
    cursor.execute("SELECT * FROM Reviews WHERE userId = %s AND movieId = %s", (session['userId'], movieId))
    if cursor.fetchone():
        return "You have already rated this movie", 400
    # Update the movie's total rating and number of ratings
    cursor.execute("""
        UPDATE Movies
        SET totalRating = totalRating + %s, numberOfRatings = numberOfRatings + 1
        WHERE movieId = %s
    """, (rating, movieId))

    conn.commit()
    cursor.execute("""
        INSERT INTO Reviews (userId, movieId, rating)
        VALUES (%s, %s, %s)
    """, (session['userId'], movieId, rating))
    conn.commit()
    cursor.close()
    conn.close()

    return '', 200
