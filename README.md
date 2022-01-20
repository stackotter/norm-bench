# NormBench

An alternative to WordBench with better crossword setting! Made on one of the rest days during NMSS

## Architecture

- Frontend: Svelte
- Backend: Python, Flask, SocketIO

## Frontend

To run the frontend, make sure to set the following three variables to the correct values (see below for some example values).

```
VITE_BACKEND_HOST=127.0.0.1
VITE_BACKEND_PORT=8000
VITE_IS_HTTPS=0
```

Run the front end using the following command:

```sh
npm run dev
```

# Backend

```sh
# Run as http
flask run --host=$VITE_BACKEND_HOST --port=$VITE_BACKEND_PORT

# Run as https
flask run --host=$VITE_BACKEND_HOST --port=$VITE_BACKEND_PORT --cert=/path/to/certfile.cert --key=/path/to/keyfile.cert
```