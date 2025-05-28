from flask import Flask, request
import threading
from src.main import main

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger_script():
    data = request.json
    print("✅ /trigger endpoint called with data:", data)  # Log this
    threading.Thread(target=run_my_script, args=(data,)).start()
    return {'status': 'Script triggered'}, 200

def run_my_script(data):
    print("Running script with:", data)
    main()
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)