from common.errors import WorkshopScheduleException

from reservation.models import Schedule


def create_schedule(workshop, start_datetime, price, capacity):
    if Schedule.objects.filter(workshop=workshop, start_datetime=start_datetime).exists():
        raise WorkshopScheduleException('schedule-duplicated')

    return Schedule.objects.create(
        workshop=workshop,
        start_datetime=start_datetime,
        price=price,
        capacity=capacity,
        seats_left=capacity,
    )

