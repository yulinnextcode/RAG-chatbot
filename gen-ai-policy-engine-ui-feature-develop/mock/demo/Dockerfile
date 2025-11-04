FROM nginx:mainline-alpine3.20-slim
 
RUN rm -rf /usr/share/nginx/html/*
COPY mock/demo/html/ /usr/share/nginx/html
COPY dist/* /usr/share/nginx/html
# Expose port 80 to access the React app
EXPOSE 80
# Start Nginx server to serve the React app
CMD ["nginx", "-g", "daemon off;"]
