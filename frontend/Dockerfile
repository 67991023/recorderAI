# Updated Dockerfile to include missing recorder.js and transcriber.js files

# Use an official Node.js runtime as a parent image
FROM node:14

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json files
COPY package*.json ./

# Install any dependencies
RUN npm install

# Copy the rest of our application code
COPY . .

# Add missing JavaScript files
COPY path/to/recorder.js ./path/to/recorder.js
COPY path/to/transcriber.js ./path/to/transcriber.js

# Expose port 3000
EXPOSE 3000

# Define the command to run our app
CMD [ "node", "dashboard.js" ]