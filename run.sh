#!/bin/bash


# Define the number of retries and the delay between retries
website_url="github.com"
max_retries=5
retry_delay=5
retries=0

# Loop to check website availability
echo "Trying to access github.com"
while [ $retries -lt $max_retries ]; do
    if ping -c 1 "$website_url"; then
        echo "Website is accessible."
        break
    else
        echo "Website is not accessible. Retrying in $retry_delay seconds..."
        sleep $retry_delay
        retries=$((retries+1))
    fi
done

# Update repository
if ping -c 1 "$website_url"; then
    sudo -u piwatts echo '' > github_error.log
    sudo -u piwatts git fetch origin 2>> github_error.log
    sudo -u piwatts git reset --hard origin/main 2>> github_error.log
else
    echo "Github.com is not accessible" >> github_error.log
fi

uvicorn main:app --reload --host 0.0.0.0 &

# Start the Svelte development server (or build your Svelte app)
cd front
npm run dev -- --host 0.0.0.0 --port 80  # Start the development server

# Use 'npm run build' for production deployment instead of 'npm run dev'