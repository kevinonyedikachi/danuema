# pull official base image
FROM python:3

# set work directory
WORKDIR /usr/src/app

# set enviroment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script into the container
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh 
RUN chmod a+x /usr/src/app/entrypoint.sh


# copy project
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Run Django's built-in development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]