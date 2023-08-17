# Modify this Procfile to fit your needs
# web: gunicorn --timeout 90 --chdir app -w 4 -k  uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 main:app
web: hypercorn -b 0.0.0.0:$PORT app/main:app