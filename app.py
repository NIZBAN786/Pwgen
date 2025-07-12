from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Main index page."""
    return jsonify({"status": "ok", "message": "Password Tools API is running"})

def run_flask():
    """Run the Flask application."""
    app.run(host='0.0.0.0', port=1100, debug=False)

if __name__ == '__main__':
    run_flask() 