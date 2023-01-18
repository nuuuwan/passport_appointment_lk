from utils import TIME_FORMAT_TIME, File, Time
from palk._common import log

class AvailabilityReport:
    def __init__(self, appointment_timeslots: list):
        self.appointment_timeslots = appointment_timeslots

    @property
    def header_lines(self):
        time_str = TIME_FORMAT_TIME.stringify(Time())
        return [
            '# Passport Application Reservation',
            f'(Compiled at {time_str})',
            '',
        ]

    @property
    def timeslot_lines(self):

        idx = {}
        for timeslot in sorted(self.appointment_timeslots, key=lambda x: x.ut):
            if not timeslot.is_available:
                continue
            application_type = timeslot.appointment_type
            location = timeslot.location
            date_str = timeslot.date_str
            if application_type not in idx:
                idx[application_type] = {}
            if location not in idx[application_type]:
                idx[application_type][location] = {}
            if date_str not in idx[application_type][location]:
                idx[application_type][location][date_str] = []
            idx[application_type][location][date_str].append(timeslot)

        lines = []
        for application_type in idx:
            lines.append(f'## {application_type}')
            for location in idx[application_type]:
                lines.append(f'### {location}')
                for date_str in idx[application_type][location]:
                    timeslots = idx[application_type][location][date_str]
                    n_appointments = len(timeslots)
                    lines.append(f'* {date_str} ({n_appointments})')

        return lines

    def save(self):

        lines = self.header_lines + self.timeslot_lines
        content = '\n'.join(lines)
        md_file_name = '/tmp/README.md'        
        File(md_file_name).write(content)
        log.info(f'Wrote report to "{md_file_name}".')
