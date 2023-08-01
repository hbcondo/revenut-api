# Modify this Procfile to fit your needs
# web: gunicorn server:app
# web: gunicorn --chdir src -w 4 -k  uvicorn.workers.UvicornWorker  main:app
web: gunicorn --timeout 90 --chdir app -w 4 -k  uvicorn.workers.UvicornWorker  main:app