from functions import *

create_tables()

@app.route('/signIn')
def signIn():
    if 'userId' in session:
        return redirect(url_for('movies'))
    
    return render_template('signIn.html')

@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/movies')
def movies():
    movies = get_movies()
    print(movies)
    return render_template('movies.html', page = 1, totalPages = get_number_of_pages(), genres=get_genres(), actors = get_actors(), languages = get_languages(), movies = movies)

@app.route('/')
def home():
    movies_overview = get_movies_overview()
    genres_stats = get_genres_stats()
    user_activity = get_user_activity()
    request_stats = get_request_stats()
    
    return render_template(
        'home.html',
        movies_overview=movies_overview,
        genres_stats=genres_stats,
        user_activity=user_activity,
        request_stats=request_stats
    )


@app.route('/watchlists')
def watchlists():
    if 'userId' not in session:
        return redirect(url_for('signIn'))

    userId = session['userId']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all watchlists for the sidebar
    cursor.execute("""
        SELECT watchlistId, name 
        FROM Watchlists 
        WHERE userId = %s 
        ORDER BY name
    """, (userId,))
    watchlists = cursor.fetchall()

    # Fetch all movies from all watchlists
    cursor.execute("""
        SELECT 
            w.name AS watchlistName,
            w.watchlistId AS watchlistId,
            m.movieId AS movieId,
            m.title,
            m.description,
            m.releaseYear,
            m.language,
            m.averageRating
        FROM WatchlistMovies wm
        JOIN Watchlists w ON wm.watchlistId = w.watchlistId
        JOIN Movies m ON wm.movieId = m.movieId
        WHERE w.userId = %s
        ORDER BY w.name, m.title
    """, (userId,))
    allWatchlistMovies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('watchlists.html', watchlists=watchlists, allWatchlistMovies=allWatchlistMovies)

@app.route('/submitRequest', methods=['GET', 'POST'])
def submitRequest():
    if request.method == 'POST':
        # Get form data
        title = request.form['title']
        description = request.form['description']
        releaseYear = request.form['releaseYear']
        directorName = request.form['directorName']
        genre = request.form['genre']
        language = request.form['language']
        directorName = request.form['directorName']
        # Validate input
        if not title or not description or not releaseYear or not genre or not language:
            flash('All fields are required!', 'error')
            return redirect(url_for('submitRequest'))
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
    INSERT INTO movierequests (userId, title, description, releaseYear, directorName, genreName, language)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", (session['userId'], title, description, releaseYear, directorName, genre, language))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('movies'))

    # If GET, show form
    if request.method == 'GET':
        # Check if user is logged in
        if 'userId' not in session:
            return redirect(url_for('signIn'))
        return render_template(
            'submitRequest.html',
            genres=get_genres(),
            languages=get_languages(),
            directors=get_directors(),
        )



app.run(host='0.0.0.0',debug=True, port=5000)
