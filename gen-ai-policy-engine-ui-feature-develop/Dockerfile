FROM nginx:mainline-alpine3.20-slim

# Remove the default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy the built React app from the previous stage to the Nginx public folder
COPY dist/* /usr/share/nginx/html
COPY mock/demo/html/ /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
# COPY ssl/* /etc/ssl

EXPOSE 443
# Start Nginx server to serve the React app
CMD ["nginx", "-g", "daemon off;"]
