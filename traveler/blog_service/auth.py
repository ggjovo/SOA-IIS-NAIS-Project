import requests

# Function to authenticate users
def authenticate_user(token):
    # Communicate with user_management service at localhost:8082
    response = requests.get('http://user-microservice:8082/checklogin', cookies={'token': token})
    if response.status_code == 200:
        return True, response.json()  # Assuming response returns user info
    else:
        return False, None