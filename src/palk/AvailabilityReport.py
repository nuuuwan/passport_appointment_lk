import os

from utils import TIMEZONE_OFFSET, File, Time, TimeFormat

from palk._common import DIR_REPO, log
from palk.AppointmentPage import URL_BASE


class AvailabilityReport:
    def __init__(self, appointment_timeslots: list):
        self.appointment_timeslots = appointment_timeslots

    @property
    def header_lines(self):
        time_str = TimeFormat(
            '%B %d, %Y (%I:%M %p)', TIMEZONE_OFFSET.LK
        ).stringify(Time())
        return [
            '# Passport Application Reservation System - Availability Report',
            f'*As of {time_str}*',
        ]

    @property
    def footer_lines(self):
        return [
            'Data Source:'
            + f' [Passport Application Reservation System]({URL_BASE})',
        ]

    @property
    def timeslot_lines(self):

        idx = {}
        for timeslot in sorted(
            self.appointment_timeslots, key=lambda x: x.ut
        ):
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
                    label = 'timeslot' if n_appointments == 1 else 'timeslots'
                    lines.append(f'* {date_str} ({n_appointments} {label})')

        return lines

    def save(self):
        lines = self.header_lines + self.timeslot_lines + self.footer_lines
        content = '\n\n'.join(lines)
        md_file_path = os.path.join(DIR_REPO, 'README.md')
        File(md_file_path).write(content)
        log.info(f'Wrote AvailabilityReport to "{md_file_path}".')


if __name__ == '__main__':
    AvailabilityReport([]).save()
