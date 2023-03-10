from dataclasses import dataclass

from utils import TIME_FORMAT_DATE, TIME_FORMAT_TIME, Time


@dataclass
class AppointmentTimeSlot:
    appointment_type: str
    location: str
    ut: float
    is_available: bool

    @property
    def to_dict(self):
        return dict(
            appointment_type=self.appointment_type,
            location=self.location,
            ut=self.ut,
            time_str=self.time_str,
            is_available=self.is_available,
        )

    @staticmethod
    def from_dict(data):
        return AppointmentTimeSlot(
            appointment_type=data['appointment_type'],
            location=data['location'],
            ut=(float)(data['ut']),
            is_available=(str(data['is_available']) == 'True'),
        )

    @property
    def time_str(self):
        return TIME_FORMAT_TIME.stringify(Time(ut=self.ut))

    @property
    def date_str(self):
        return TIME_FORMAT_DATE.stringify(Time(ut=self.ut))
