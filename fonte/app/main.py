from http import HTTPStatus

from fastapi import FastAPI

from app.api.v1.endpoints import seeds, sensor

app = FastAPI(title='Fonte API - Desafio ETL')

app.include_router(sensor.router, prefix='/api', tags=['Dados Fonte'])
app.include_router(seeds.router, prefix='/api', tags=['Seeds'])


@app.get('/health', status_code=HTTPStatus.OK)
async def health_check():
    return {'status': 'ok'}
