# Architecture

## Auth model

- Email + password credentials, hashed with bcrypt (cost factor 12)
- Sessions represented as signed JWTs, not server-side session storage
- Password reset uses a short-lived, single-use token emailed to the user

## Why JWT, not sessions

Chosen for statelessness across the two app instances behind the load
balancer, avoiding a shared session store for a small internal tool. Revisit
if the app grows a "log out everywhere" requirement.

## Files

- `src/models/user.ts` - User model and migration
- `src/routes/auth.ts` - registration, login, password reset routes
