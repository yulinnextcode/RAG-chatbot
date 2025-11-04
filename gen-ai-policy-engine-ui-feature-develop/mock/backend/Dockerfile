FROM node:20.17-slim

WORKDIR /app
COPY mock/backend/ ./
COPY dist/ ./public
RUN npm install
 

# Expose the port your Express app listens on
EXPOSE 80

CMD ["npm", "run", "start"] 