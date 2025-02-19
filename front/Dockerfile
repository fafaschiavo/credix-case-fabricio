# Use an official Node.js image as base
FROM node:18

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install  # Install dependencies

# Copy the rest of the frontend code
COPY . .

# Expose the new Vite port
EXPOSE 8001