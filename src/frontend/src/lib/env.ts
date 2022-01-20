export const variables = {
    backendHost: import.meta.env.VITE_BACKEND_HOST,
    backendPort: import.meta.env.VITE_BACKEND_PORT,
    backendIsHttps: import.meta.env.VITE_BACKEND_IS_HTTPS == true,
};

export const backendURL = `${variables.backendIsHttps ? "https" : "http"}://${variables.backendHost}:${variables.backendPort}`