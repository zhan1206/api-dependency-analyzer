# Example: JavaScript/TypeScript API calls
# This file demonstrates various API call patterns

// REST API calls
const API_BASE = 'https://api.github.com';
const usersUrl = 'https://api.github.com/users';

fetch('https://api.github.com/users/octocat')
  .then(response => response.json())
  .then(data => console.log(data));

// Axios calls
axios.get('https://api.openai.com/v1/models', {
  headers: { 'Authorization': `Bearer ${API_KEY}` }
});

axios.post('https://api.stripe.com/v1/customers', {
  email: 'customer@example.com'
}, {
  auth: { username: 'sk_test_xxx', password: '' }
});

// WebSocket
const ws = new WebSocket('wss://api.example.com/realtime');

// GraphQL with Apollo
const { gql } = require('@apollo/client');
const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
      email
    }
  }
`;

// Insecure HTTP call (BAD PRACTICE!)
http.get('http://insecure-api.example.com/data', (res) => {
  console.log('Response:', res);
});

// Environment variables
const STRIPE_KEY = process.env.STRIPE_SECRET_KEY;
const GH_TOKEN = process.env.GITHUB_TOKEN;
