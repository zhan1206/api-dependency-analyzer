# Example: Python API calls
# This file demonstrates various API call patterns

import requests
import httpx
from gql import gql, Client, transport

# REST API calls
response = requests.get('https://api.github.com/users')
users = response.json()

# Axios-like HTTP calls
async with httpx.AsyncClient() as client:
    response = await client.get(
        'https://api.openai.com/v1/models',
        headers={'Authorization': f'Bearer {API_KEY}'}
    )

# GraphQL client
client = Client(
    transport=HTTPTransport(url='https://countries.trevorblades.com/graphql'),
    fetch_impl=fetch
)

query = gql('''
    query GetCountries {
        countries {
            code
            name
        }
    }
''')

# Third-party API calls
stripe_response = requests.post(
    'https://api.stripe.com/v1/charges',
    data={'amount': 1000, 'currency': 'usd'},
    auth=('sk_test_xxx', '')
)

# Weather API
weather = requests.get(
    'https://api.openweathermap.org/data/2.5/weather',
    params={'q': 'Beijing', 'appid': API_KEY}
)

# Database-like API
db_response = httpx.get(
    'https://api.example.com/records',
    timeout=30.0
)
