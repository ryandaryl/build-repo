
import os
from flask import Flask, send_from_directory, render_template
app = Flask(__name__, template_folder='')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
