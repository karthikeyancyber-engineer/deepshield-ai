from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.detection import TrustScoreRequest, TrustScoreResponse
from app.services.trust_score import TrustScoreService

router = APIRouter(prefix="/trust", tags=["Trust Score"])


@router.post(
    "/score",
    response_model=TrustScoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Compute composite trust score",
    description="Aggregate face, voice, lip-sync, and emotion detections into a single trust score with risk assessment.",
)
async def compute_trust_score(
    request: TrustScoreRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await TrustScoreService.compute(db, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
