// Google services that Firebase sign-in (signInWithPopup) talks to.
export const FIREBASE_CONNECT_ORIGINS = [
  "https://identitytoolkit.googleapis.com",
  "https://securetoken.googleapis.com",
  "https://www.googleapis.com",
  "https://apis.google.com",
]

// Paddle's checkout runs in a frame from these, and Paddle.js talks to them.
export const PADDLE_ORIGINS = ["https://*.paddle.com"]

// Profile photos of Google accounts.
export const ACCOUNT_IMAGE_ORIGINS = ["https://*.googleusercontent.com"]

// Sentry: share of page loads and requests traced for performance.
export const SENTRY_TRACES_SAMPLE_RATE = 0.1
