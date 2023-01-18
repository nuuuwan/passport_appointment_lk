from utils import TIME_FORMAT_TIME, File, Time

from palk._common import log

MD_FILE_NAME = 'README.md'


class AvailabilityReport:
    def __init__(self, appointment_timeslots: list):
        self.appointment_timeslots = appointment_timeslots

    @property
    def header_lines(self):
        time_str = TIME_FORMAT_TIME.stringify(Time())
        return [
            '# Passport Application Reservation',
            f'## (Compiled at {time_str})',
            '',
        ]

    @property
    def timeslot_lines(self):
        lines = []
        for timeslot in self.appointment_timeslots:
            if not timeslot.is_available:
                continue
            lines.append(
                f'* {timeslot.appointment_type} - {timeslot.location} -'
                + f'{timeslot.time_str}'
            )

        return lines

    def save(self):

        lines = self.header_lines + self.timeslot_lines
        content = '\n'.join(lines)
        File(MD_FILE_NAME).write(content)
        log.debug(f'Wrote report to {MD_FILE_NAME}')
