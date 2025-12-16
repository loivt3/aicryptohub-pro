# Admin Console Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Serve with preview mode (or use nginx for production)
EXPOSE 3001

# For development
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
