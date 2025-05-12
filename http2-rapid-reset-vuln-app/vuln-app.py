from flask import Flask, request, jsonify
import time
import os
import base64
import random
import multiprocessing

app = Flask(__name__)

@app.route('/big_body')
def big_body():
    # Return a large response
    return 'a' * 1000000

@app.route('/')
def root():
    return 'Hello, World!'


@app.route('/random_text', methods=['GET'])
def random_text():
    # Get configurable parameters (min_size and max_size)
    min_size = int(request.args.get('min_size', 1024))  # Default to 1024 bytes
    max_size = int(request.args.get('max_size', 1048576))  # Default to 1 MB (2**20 bytes)

    # Ensure min_size is not greater than max_size
    if min_size > max_size:
        min_size = max_size

    # Generate random data size between min_size and max_size
    expected_size = random.randint(min_size, max_size)

    # Read from /dev/urandom and encode in base64
    random_bytes = os.urandom(expected_size)
    base64_encoded = base64.b64encode(random_bytes).decode('utf-8')

    # Prepare response data with exponential probability for size adjustment
    if random.random() > 0.5:
        # If random check passes, adjust the size and parameters
        get_params = {'min_words': 1, 'max_words': expected_size}
        route = "/random"
        route += "?" + "&".join([f"{k}={v}" for k, v in get_params.items()])
    else:
        route = "/random"
    size_in_mb = expected_size / 1024**2
    print(f"Returning {size_in_mb} Mbytes of random data")
    return jsonify({
        "random_base64": base64_encoded,
        "size": expected_size,
        "route": route
    })

# If 404, use random_text()
@app.errorhandler(404)
def page_not_found(e):
    return random_text()

@app.route('/slow/<int:seconds>')
def slow(seconds):
    time.sleep(seconds)
    return jsonify({"message": f"Slept for {seconds} seconds."})

# Function to stress the CPU
def cpu_stress(duration):
    # Simple CPU-bound task: calculate prime numbers in a loop
    def calculate_primes():
        primes = []
        for num in range(2, 10000):
            if all(num % i != 0 for i in range(2, int(num ** 0.5) + 1)):
                primes.append(num)
        return primes
    
    start_time = time.time()
    while time.time() - start_time < duration:
        calculate_primes()  # Keep the CPU busy

def stress_cpu(stress_level, duration):
    # stress_level: number of processes to use
    # duration: how long the stress test runs (in seconds)
    processes = []
    for _ in range(stress_level):
        process = multiprocessing.Process(target=cpu_stress, args=(duration,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
    return "CPU stress test completed."

@app.route('/cpu_stress/<int:stress_level>/<int:duration>')
def cpu_stress_route(stress_level, duration):
    # Stress the CPU with the specified stress level and duration
    stress_cpu(stress_level, duration)
    return jsonify({"message": f"CPU stress test completed with {stress_level} processes for {duration} seconds."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)