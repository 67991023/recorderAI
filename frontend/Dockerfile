FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy all static files (HTML, CSS, JS)
COPY index.html   /usr/share/nginx/html/
COPY styles.css   /usr/share/nginx/html/
COPY api.js       /usr/share/nginx/html/
COPY charts.js    /usr/share/nginx/html/
COPY dashboard.js /usr/share/nginx/html/

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]