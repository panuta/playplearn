
from reservation.models import Schedule


def create_schedule(workshop, start_datetime, price, capacity):
    return Schedule.objects.create(
        workshop=workshop,
        start_datetime=start_datetime,
        price=price,
        capacity=capacity,
        seats_left=capacity,
    )

