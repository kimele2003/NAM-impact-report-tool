from flask import Flask, request
import threading

app = Flask(__name__)

# @app.route('/trigger', methods=['POST'])
# def trigger_script():
#     data = request.json
#     print("Received from Airtable:", data)
#     return {'status': 'OK'}, 200

@app.route('/trigger', methods=['POST'])
def trigger_script():
    data = request.json
    threading.Thread(target=run_my_script, args=(data,)).start()
    return {'status': 'Script triggered'}, 200

def run_my_script(data):
    print("Running script with:", data)
    # Your existing logic here

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)