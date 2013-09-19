from common.errors import WorkshopScheduleException

from reservation.models import Schedule, Reservation


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


def create_reservation(schedule, people, price, user):
    total = people * price

    return Reservation.objects.create(
        user=user,
        schedule=schedule,
        price=price,
        seats=people,
        total=total,
        payment_status=Reservation.PAYMENT_STATUS_WAIT_FOR_PAYMENT,
    )