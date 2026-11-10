FROM python:3.14-slim
WORKDIR /app
COPY servidor.py perguntas.txt ./
EXPOSE 5000
CMD ["python", "-u", "servidor.py"]
