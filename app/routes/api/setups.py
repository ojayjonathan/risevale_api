from typing import List, Optional

from fastapi import APIRouter, Body
from fastapi.params import Query, Depends

from app import schema
from app.models import User
from app.repository.base import SearchModel
from app.repository.setups import country_repository, city_repository
from app.routes.deps import SessionDep, current_user
from app.schema import SortModel

router = APIRouter(prefix="/setups", tags=["setups"])


@router.get("/countries/", response_model=List[schema.Country])
def countries(db=SessionDep):
    return country_repository.get_all(
        db=db, sort=SortModel(sort="name", direction="asc")
    )


@router.post("/countries/", response_model=schema.Country)
def create_country(
    db=SessionDep,
    country: schema.CountryCreate = Body(...),
    user: User = Depends(current_user),
):
    return country_repository.create(
        db=db,
        item=country,
        audit_user_id=user.id,
    )


@router.put("/countries/{id}", response_model=schema.Country)
def update_country(
    id: int,
    country: schema.CountryCreate,
    db=SessionDep,
    user: User = Depends(current_user),
):
    return country_repository.update(
        db=db,
        current_item=country_repository.get_object_or_404(db=db, id=id),
        item_in=country,
        audit_user_id=user.id,
    )


@router.delete("/countries/{id}", response_model=schema.Country)
def delete_country(
    id: int,
    db=SessionDep,
    user: User = Depends(current_user),
):
    return country_repository.delete(
        db=db,
        id=id,
        audit_user_id=user.id,
    )


@router.get("/cities/", response_model=List[schema.City])
def cities(
    db=SessionDep,
    q: Optional[str] = Query(None),
    country_id: Optional[int] = Query(None),
):
    filters = {}

    if country_id:
        filters["country_id"] = country_id

    search = None
    if q:
        search = SearchModel(search_query=q, search_fields=["name"])

    return city_repository.get_all(
        db=db, search=search, sort=SortModel(sort="name", direction="asc"), **filters
    )


@router.post("/cities/", response_model=schema.City)
def create_cities(
    db=SessionDep, city: schema.CityCreate = Body(), user: User = Depends(current_user)
):
    return city_repository.create(db=db, item=city, audit_user_id=user.id)


@router.put("/cities/{id}", response_model=schema.City)
def update_cities(
    id: int,
    city: schema.CityCreate,
    user: User = Depends(current_user),
    db=SessionDep,
):
    return city_repository.update(
        db=db,
        current_item=city_repository.get_object_or_404(db=db, id=id),
        item_in=city,
        audit_user_id=user.id,
    )


@router.delete("/cities/{id}", response_model=schema.City)
def delete_cities(
    id: int,
    db=SessionDep,
    user: User = Depends(current_user),
):
    return city_repository.delete(
        db=db,
        id=id,
        audit_user_id=user.id,
    )
