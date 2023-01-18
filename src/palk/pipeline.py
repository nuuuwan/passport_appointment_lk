import os

from utils import JSONFile

from palk.AppointmentPage import AppointmentPage
from palk.AppointmentTimeSlot import AppointmentTimeSlot
from palk.AvailabilityReport import AvailabilityReport

DATA_FILE_NAME = 'data.json'

if __name__ == '__main__':
    if not os.path.exists(DATA_FILE_NAME):
        page = AppointmentPage()
        page.set_application_type('One Day Service')
        page.set_location('HEAD OFFICE - BATTARAMULLA')
        appointment_timeslots = page.get_available_timeslots()

        data_list = [
            appointment_timeslot.to_dict
            for appointment_timeslot in appointment_timeslots
        ]
        JSONFile(DATA_FILE_NAME).write(data_list)
    else:
        data_list = JSONFile(DATA_FILE_NAME).read()

    appointment_timeslots = [
        AppointmentTimeSlot.from_dict(data) for data in data_list
    ]
    report = AvailabilityReport(appointment_timeslots)
    report.save()
