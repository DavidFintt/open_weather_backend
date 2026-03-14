from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check():
    pass


@app.get("/weather")
def get_weather():
    pass
