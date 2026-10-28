# Troubleshooting

## `docker` or `docker compose` not found
Install/start Docker Desktop (Windows/macOS) or Docker Engine + Compose (Linux), then reopen the terminal.

## Port 3000, 5432, or 8000 is already in use
Stop the other service or change the host-side port mapping in `docker-compose.yml`. If you change the frontend/API ports, update `NEXT_PUBLIC_API_URL`, CORS origins, and callback URLs consistently.

## Database connection refused
Use the Compose service hostname `db` in `DATABASE_URL` inside Docker, not `localhost`. Wait for the database health check, then inspect `docker compose logs db api`.

## Frontend cannot reach API
Check that `NEXT_PUBLIC_API_URL` is reachable from the browser (usually `http://localhost:8000`) and that the API CORS origin includes the exact frontend origin. Rebuild the frontend container after changing build-time public variables if required.

## Provider says callback/IPN unreachable
Provider servers cannot access `localhost` on your laptop. Set `PAYMENT_PUBLIC_BASE_URL` to a public HTTPS API URL from a trusted development tunnel or deployed test environment, and configure the callback/IPN URL according to the provider docs. Do not expose your development server without access controls.

## Payment options say credentials are missing
That is expected until sandbox credentials are obtained and set in `.env`. Ensure the names match `.env.example`, credentials remain backend-only, and restart with `docker compose up --build`. Never paste credentials into chat, screenshots, or source files.

## Dependency install/build fails
Confirm network access to package registries, compatible Python/Node versions, and retry the relevant install command. Read the full first error rather than only the final summary. Check `docker compose logs --tail=200 api frontend`.

## Demo data needs reset
`docker compose down -v` removes the database volume and all local data. Use only if you are comfortable losing local work.
