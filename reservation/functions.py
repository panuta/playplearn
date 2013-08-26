
from reservation.models import Schedule


def create_schedule(workshop, start_datetime, price, total_seats):
    return Schedule.objects.create(
        workshop=workshop,
        start_datetime=start_datetime,
        price=price,
        total_seats=total_seats,
        seats_left=total_seats,
    )

