const currentDomain = window.location.hostname;

let apiBaseUrl: string;
if (currentDomain === 'localhost') {
  apiBaseUrl = 'http://localhost:8000';
} else {
  apiBaseUrl = 'https://api.credix.pixelbreeders.com';
}

export const API_BASE_URL: string = apiBaseUrl;