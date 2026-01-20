from fastapi import APIRouter

from .api import (
    auth,
    activities,
    setups,
    destinations,
    hotels,
    tour,
    tour_day,
    tour_booking,
)

router = APIRouter()

router.include_router(auth.router)
router.include_router(activities.router)
router.include_router(setups.router)
router.include_router(destinations.router)
router.include_router(hotels.router)
router.include_router(tour.router)
router.include_router(tour_day.router)
router.include_router(tour_booking.router)
