from adminFunctions import *

@app.route('/adminSignUp')
def adminSignUp():
    return render_template('adminSignUp.html')

@app.route('/adminSignIn')
def adminSignIn():
    if 'userId' in session:
        return redirect(url_for('adminHome'))
    
    return render_template('adminSignIn.html')

@app.route('/editRequest', methods=['GET', 'POST'])
def editRequest():
    if 'userId' not in session:
        return redirect(url_for('adminSignIn'))

    if request.method == 'POST':
        data = request.get_json()
        requestId = data.get('requestId')
    else:
        requestId = request.args.get('requestId')

    if not requestId:
        return "Request ID is required", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM movierequests WHERE requestId = %s", (requestId,))
        requestData = cursor.fetchone()

        if not requestData:
            return "Request not found", 404

        # Load languages and genres
        languages = get_languages()
        genres = get_genres()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'editRequest.html',
        requestData=requestData,
        languages=languages,
        genres=genres
    )



@app.route('/')
def adminHome():
    movieRequests = get_movierequest()
    if 'userId' in session:
        return render_template('adminHome.html', page = 1, totalPages= get_number_of_pages(), requests=movieRequests, actors=get_actors())
    else:
        return redirect(url_for('adminSignIn'))

app.run(host='0.0.0.0',debug=True, port=8080)
