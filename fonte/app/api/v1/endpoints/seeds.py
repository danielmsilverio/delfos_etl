from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.seed import SeedRequest
from app.services.seeder import DataSeeder

router = APIRouter()


@router.post('/seed', status_code=201)
async def seed_database(
    payload: SeedRequest,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Endpoint para popular o banco de dados.
    """
    seeder = DataSeeder(db)
    try:
        result = await seeder.generate_data(payload.start_date, payload.days)
        return {'message': 'Dados inseridos com sucesso', 'details': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
