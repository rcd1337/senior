"""Preço da estadia: diária, vaga e taxa de check-out após as 12h."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal

WEEKDAY_DAILY = Decimal("120.00")
WEEKEND_DAILY = Decimal("180.00")
WEEKDAY_PARKING = Decimal("15.00")
WEEKEND_PARKING = Decimal("20.00")
CHECKIN_FROM = time(14, 0)
CHECKOUT_UNTIL = time(12, 0)


def is_weekend(day: date) -> bool:
    return day.weekday() >= 5


def daily_rate(day: date) -> Decimal:
    return WEEKEND_DAILY if is_weekend(day) else WEEKDAY_DAILY


def parking_rate(day: date) -> Decimal:
    return WEEKEND_PARKING if is_weekend(day) else WEEKDAY_PARKING


def stay_dates(check_in: date, check_out: date) -> list[date]:
    """Noites cobradas: do check-in até o dia anterior ao check-out.

    Estadia de um único dia gera uma diária.
    """
    if check_out <= check_in:
        return [check_in]
    days = []
    current = check_in
    while current < check_out:
        days.append(current)
        current += timedelta(days=1)
    return days


def checkin_alert(moment: datetime) -> str | None:
    """Alerta se o check-in é antes das 14h. O procedimento não é bloqueado."""
    if moment.time() < CHECKIN_FROM:
        return (
            "Check-in permitido a partir das 14h00. "
            "O procedimento foi registrado antes do horário previsto."
        )
    return None


def late_checkout_fee(checkout_at: datetime) -> Decimal:
    """Metade da diária do dia do check-out se passar das 12h; caso contrário, zero."""
    if checkout_at.time() <= CHECKOUT_UNTIL:
        return Decimal("0.00")
    return (daily_rate(checkout_at.date()) * Decimal("0.5")).quantize(Decimal("0.01"))


def build_bill(check_in: date, check_out: date, has_car: bool, checkout_at: datetime) -> dict:
    """Itens por noite, taxa tardia e total. Valores monetários em string."""
    items = []
    total = Decimal("0.00")
    for day in stay_dates(check_in, check_out):
        daily = daily_rate(day)
        parking = parking_rate(day) if has_car else Decimal("0.00")
        subtotal = daily + parking
        items.append(
            {
                "date": day.isoformat(),
                "daily": str(daily),
                "parking": str(parking),
                "subtotal": str(subtotal),
            }
        )
        total += subtotal

    late_fee = late_checkout_fee(checkout_at)
    total += late_fee
    return {
        "items": items,
        "late_checkout_fee": str(late_fee),
        "total": str(total.quantize(Decimal("0.01"))),
    }
