from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('start.html')

@app.route('/search', methods=['POST'])
def search():
    print request.form
    return render_template('start.html')

if __name__ == "__main__":
	app.run()