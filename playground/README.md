# Agent Translator Playground

This is the zero-backend, static playground for experimenting with the Agent Translator Middleware.

## Run locally

```bash
npm install
npm run dev
```

## Configure the API

The playground calls a public demo instance of the middleware. Configure it in one of two ways:

- Set `VITE_PLAYGROUND_API_BASE` in your environment.
- Or paste the API base URL in the UI.

The default endpoint is `/api/v1/beta/playground/translate`. Override it with
`VITE_PLAYGROUND_ENDPOINT` if you want a different route.

## Shareable URLs

The playground stores the source JSON and protocol selection in the URL hash as a Base64 blob.
Copy the share link from the UI to send the exact scenario to someone else.
