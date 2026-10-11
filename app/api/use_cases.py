
from fastapi import APIRouter, HTTPException, status

from app.models.use_case import UseCaseConfig

router = APIRouter(prefix="/use-cases", tags=["Use Cases"])

# Temporary storage. We will replace this with a database later.
_use_cases: dict[str, UseCaseConfig] = {}

def find_use_case(use_case_id: str) -> UseCaseConfig | None:
    """Return a registered use case, if it exists."""
    return _use_cases.get(use_case_id)

@router.post(
    "",
    response_model=UseCaseConfig,
    status_code=status.HTTP_201_CREATED,
)
async def create_use_case(config: UseCaseConfig) -> UseCaseConfig:
    if config.use_case_id in _use_cases:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A use case with this ID already exists.",
        )

    _use_cases[config.use_case_id] = config
    return config


@router.get("", response_model=list[UseCaseConfig])
async def list_use_cases() -> list[UseCaseConfig]:
    return list(_use_cases.values())


@router.get("/{use_case_id}", response_model=UseCaseConfig)
async def get_use_case(use_case_id: str) -> UseCaseConfig:
    config = _use_cases.get(use_case_id)

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Use case not found.",
        )

    return config
