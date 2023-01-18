import os

from utils import TIME_FORMAT_TIME_ID, Time, TSVFile

from palk.AppointmentPage import AppointmentPage
from palk.AppointmentTimeSlot import AppointmentTimeSlot
from palk.AvailabilityReport import AvailabilityReport

DATA_FILE_NAME = 'data/data.tsv'

if __name__ == '__main__':
    time_id = TIME_FORMAT_TIME_ID.stringify(Time())
    page = AppointmentPage()
    page.set_application_type('One Day Service')
    page.set_location('HEAD OFFICE - BATTARAMULLA')
    appointment_timeslots = page.get_available_timeslots()

    data_list = [
        appointment_timeslot.to_dict
        for appointment_timeslot in appointment_timeslots
    ]
    TSVFile(DATA_FILE_NAME).write(data_list)
    history_data_file_name = os.path.join(f'data/data.{time_id}.tsv')
    TSVFile(history_data_file_name).write(data_list)

    appointment_timeslots = [
        AppointmentTimeSlot.from_dict(data) for data in data_list
    ]
    report = AvailabilityReport(appointment_timeslots)
    report.save()
