FROM node:alpine as frontend-build

# install deps
RUN mkdir /build
ADD /frontend/package*.json /build/
WORKDIR /build
RUN npm install

# compile
ADD /frontend/ /build/
RUN npm run build

###############################

FROM python:3.6-jessie

# install deps
RUN mkdir /app /app/static
ADD /backend/requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

# install app
ADD /backend /app
COPY --from=frontend-build /build/dist/ /app/static/

ENV FLASK_APP=server.py
CMD ["flask", "run", "-h", "0.0.0.0"]
