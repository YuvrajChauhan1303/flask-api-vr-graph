from flask import Flask, request, send_file, jsonify
import matplotlib.pyplot as plt
import numpy as np
import io
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for readings
readings = []

@app.route('/storeReading', methods=['POST'])
def store_reading():
    data = request.json
    voltage = data.get('voltage')
    current = data.get('current')
    if voltage is not None and current is not None:
        readings.append((float(current), float(voltage)))  # (x=current, y=voltage)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid input'}), 400

@app.route('/clearReadings', methods=['POST'])
def clear_readings():
    readings.clear()
    return jsonify({'success': True, 'message': 'Readings cleared'})

@app.route('/plotGraph', methods=['GET'])
def plot_graph():
    if len(readings) < 2:
        return jsonify({'error': 'Not enough data points'}), 400

    # Separate currents (x) and voltages (y)
    currents = np.array([r[0] for r in readings])
    voltages = np.array([r[1] for r in readings])

    # Linear regression (y = mx + b)
    coeffs = np.polyfit(currents, voltages, 1)
    slope = coeffs[0]
    intercept = coeffs[1]
    fit_line = slope * currents + intercept

    # Plot
    plt.figure(figsize=(6, 4))
    plt.scatter(currents, voltages, label='Data Points', color='blue')
    plt.plot(currents, fit_line, label=f'Fit Line (R = {slope:.2f} Ω)', color='red')
    plt.xlabel('Current (A)')
    plt.ylabel('Voltage (V)')
    plt.title('Voltage vs Current')
    plt.legend()
    plt.grid(True)

    # Save image to memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    # Host on 0.0.0.0 to allow LAN access
    app.run(host='0.0.0.0', port=5000, debug=False)
