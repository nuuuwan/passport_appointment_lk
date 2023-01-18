
from utils import File
class AvailabilityReport:
    def __init__(self, appointment_timeslot_list: list):
        self.appointment_timeslot_list = appointment_timeslot_list

    def save(self):
        md_file_name = 'README.md'

        lines = [
            '# Passport Application Reservation', 
            '',
        ]
        content = '\n\n'.join(lines)

