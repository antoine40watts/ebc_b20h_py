#!/bin/bash

# Update repository
if ping -c 1 "github.com"; then
    > error.log
    git fetch origin 2>> error.log
    git reset --hard origin/main 2>> error.log
else
    echo "Github.com is not accessible" >> error.log
fi

uvicorn main:app --reload --host 0.0.0.0 &

# Start the Svelte development server (or build your Svelte app)
cd front
npm run dev -- --host 0.0.0.0 --port 80  # Start the development server

# Use 'npm run build' for production deployment instead of 'npm run dev'