@app.route('/', methods=['GET'])
def index():
    items = get_all_metadata()
    return render_template('BuyRoll.html', items=items)