FROM python:3.9
COPY requirements .
RUN pip install -r requirements
COPY . .
CMD uvicorn --factory app.server:start_app --loop uvloop --workers 2
