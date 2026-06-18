FROM node:20-alpine

# Install sqlite3 dependencies for node-sqlite3
RUN apk add --no-cache python3 make g++ sqlite

WORKDIR /app

# Copy package files
COPY server/package*.json ./

# Install dependencies (rebuilds sqlite3 for Alpine architecture)
RUN npm install

# Copy application files
# We copy public/ into /app/public and server/ into /app/server
COPY public ./public
COPY server ./server

WORKDIR /app/server

# Expose the API port
EXPOSE 8086

# Start the server
CMD ["node", "server.js"]
