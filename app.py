from flask import Flask, jsonify, request
import requests
from collections import deque
import time

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
SERVER_URLS = {
    'p': 'http://20.244.56.144/test/primes',
    'f': 'http://20.244.56.144/test/fibo',
    'e': 'http://20.244.56.144/test/even',
    'r': 'http://20.244.56.144/test/rand'
}
AUTH_URL = 'http://20.244.56.144/test/auth'
CLIENT_ID = 'f477c03e-4e0c-4da7-858b-6260b00a1b09'
CLIENT_SECRET = 'zErCQOlhUeVXpErg'
AUTH_PAYLOAD = {
    "companyName": "goMart",
    "clientID": CLIENT_ID,
    "clientSecret": CLIENT_SECRET,
    "ownerName": "Ranjan GR",
    "ownerEmail": "Ranjanmalode2001@gmail.com",
    "rollNo": "R22EJ810"
}

# Store numbers in a deque to maintain window size
stored_numbers = deque(maxlen=WINDOW_SIZE)
auth_token = None

def get_auth_token():
    global auth_token
    try:
        response = requests.post(AUTH_URL, json=AUTH_PAYLOAD)
        if response.status_code == 200 or response.status_code == 201:
            auth_token = response.json().get('access_token')
            if auth_token:
                print(f"Obtained auth token: {auth_token}")
            else:
                print("Auth token not found in the response.")
        else:
            print(f"Failed to obtain auth token: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.RequestException as e:
        print(f"Auth request failed: {e}")

def fetch_numbers(type_id):
    if not auth_token:
        print("No auth token available")
        return []

    url = SERVER_URLS.get(type_id)
    if not url:
        print(f"Invalid URL for type ID: {type_id}")
        return []

    headers = {
        'Authorization': f'Bearer {auth_token}'
    }

    try:
        for _ in range(3):  # Retry up to 3 times
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=0.5)
            response_time = time.time() - start_time
            print(f"Fetched numbers from {url} in {response_time:.2f} seconds")

            if response_time > 0.5:
                print(f"Response took too long: {response_time:.2f} seconds")
                continue

            if response.status_code == 200:
                numbers = response.json().get('numbers', [])
                print(f"Numbers fetched: {numbers}")
                return numbers
            else:
                print(f"Received non-200 status code: {response.status_code}")
                print(f"Response: {response.text}")
                if response.status_code == 503:
                    time.sleep(1)  # Wait for a second before retrying
                else:
                    return []
    except requests.Timeout:
        print("Request timed out")
    except requests.RequestException as e:
        print(f"Request failed: {e}")

    return []

@app.route('/numbers/<type_id>', methods=['GET'])
def get_numbers(type_id):
    if type_id not in SERVER_URLS:
        return jsonify({'error': 'Invalid type ID'}), 400

    # Fetch numbers from third-party server
    new_numbers = fetch_numbers(type_id)
    
    if new_numbers:
        # Remove duplicates from new_numbers
        new_numbers = [num for num in new_numbers if num not in stored_numbers]
        # Update stored numbers with the new numbers
        prev_state = list(stored_numbers)
        stored_numbers.extend(new_numbers)
        curr_state = list(stored_numbers)

        # Calculate average
        avg = sum(stored_numbers) / len(stored_numbers) if stored_numbers else 0

        response = {
            'windowPrevState': prev_state,
            'windowCurrState': curr_state,
            'numbers': new_numbers,
            'avg': round(avg, 2)
        }
    else:
        response = {
            'windowPrevState': list(stored_numbers),
            'windowCurrState': list(stored_numbers),
            'numbers': [],
            'avg': 0
        }

    return jsonify(response)

@app.route('/', methods=['GET'])
def index():
    return "Welcome to the Average Calculator Microservice. Use /numbers/<type_id> to fetch numbers.", 200

if __name__ == '__main__':
    get_auth_token()  # Fetch the token on startup
    app.run(host='0.0.0.0', port=9876)
