# Production Nginx container for Latha Oils Storefront
FROM nginx:alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy application files
COPY . /usr/share/nginx/html

# Expose standard web port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
