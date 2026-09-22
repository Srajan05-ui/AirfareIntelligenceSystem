# Step 1: Build the React Application
FROM node:20-alpine AS build

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# Copy all frontend files
COPY frontend/ ./
# Build the production optimized files
RUN npm run build

# Step 2: Serve via NGINX
FROM nginx:alpine

# Copy the build output to replace the default nginx contents
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
