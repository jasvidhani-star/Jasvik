FROM node:20-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg imagemagick curl ca-certificates &&     apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN npm install -g n8n
EXPOSE 5678
CMD ["n8n"]
