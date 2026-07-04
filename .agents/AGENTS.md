# Docker Compose & .env Management Rules

When working with Docker Compose and `.env` files, follow these strict rules to avoid "stale environment" bugs:

## 1. The Trap of `docker compose restart`
**NEVER** use `docker compose restart` when you have modified the `.env` file or the `docker-compose.yml`. 
- `restart` only stops and starts the *existing* container instance.
- It **does not** read the updated `.env` file. The container will boot using the old variables locked in its memory from when it was first created.

## 2. The Correct Workflow for `.env` Changes
To apply changes made to a `.env` file, you **MUST** recreate the container:
```bash
docker compose up -d <service_name>
```
- This command detects that the environment variables or configuration have changed and safely destroys the old container to create a new one with the updated values.

## 3. Rebuilding Images
If you change `requirements.txt`, `Dockerfile`, or any file that is copied into the image during the build process (and not mounted via volumes), you must force a rebuild:
```bash
docker compose up --build -d <service_name>
```

## 4. Handling Docker DNS/Network Failures (Fallback)
If `docker compose up --build -d` fails due to network or DNS timeouts (common Docker Desktop bug on Mac):
1. Run `docker compose up -d <service_name>` (without `--build`) to at least recreate the container so it picks up the new `.env` variables.
2. Manually install the dependencies inside the running container as a bypass: `docker compose exec <service_name> pip install <package>`.
3. Finally, run `docker compose restart <service_name>` so the application reloads with the manually installed dependencies.
