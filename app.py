from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wifi')
def wifi():
    return render_template('wifi_config.html')

@app.route('/placeholder')
def placeholder():
    return "This is a placeholder for future pages."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)