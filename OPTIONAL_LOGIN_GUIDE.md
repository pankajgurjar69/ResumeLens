# Optional Login – ResumeLens

## User choices
- **Continue as guest:** no account needed; reports are saved against a random browser-session key.
- **Create account:** name, email and password (minimum 8 characters).
- **Sign in / Sign out:** each account sees only analyses saved under its own user ID.

## Routes
- `/register` – create account
- `/login` – sign in
- `/logout` – sign out (POST)
- `/dashboard` – guest or signed-in workspace

## Test manually
1. Open the app in a private/incognito browser window.
2. Continue as guest and check that the dashboard loads.
3. Create a test account using a test email and a unique, non-sensitive password.
4. Sign out, then sign in again.
5. Run an analysis while signed in and check History.
6. Open another private window as a guest; it should not show the account's reports.

## Current prototype limitations
There is no email verification, password reset, account deletion flow, CSRF protection, login rate limiting or automatic transfer of guest history into a new account. Add and test these before public production use. The app hashes passwords with Werkzeug's password hashing helpers.
