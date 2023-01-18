from dataclasses import dataclass

from utils import TIME_FORMAT_TIME, Time


@dataclass
class AppointmentTimeSlot:
    appointment_type: str,
    location: str,
    ut: float
    is_available: bool

    @property
    def to_dict(self):
        return dict(
            appointment_type=self.appointment_type,
            location=self.location,
            ut=self.ut,
            time_str=TIME_FORMAT_TIME.stringify(Time(self.ut)),
            is_available=self.is_available,
        )
