import os

from utils import SECONDS_IN, TIME_FORMAT_TIME_ID, Time, TimeDelta, TSVFile

from palk._common import log
from palk.AppointmentPage import AppointmentPage
from palk.AppointmentTimeSlot import AppointmentTimeSlot
from palk.AvailabilityReport import AvailabilityReport

DATA_FILE_NAME = 'data/data.tsv'
N_DAYS = 60
FORCE_SCRAPE = True

if __name__ == '__main__':
    if not os.path.exists(DATA_FILE_NAME) or FORCE_SCRAPE:
        all_timeslots = AppointmentPage.get_all_timeslots()    
        data_list = [
            x.to_dict
            for x in all_timeslots
        ]
        time_id = TIME_FORMAT_TIME_ID.stringify(time_now)
        TSVFile(DATA_FILE_NAME).write(data_list)
        history_data_file_name = os.path.join(f'data/data.{time_id}.tsv')
        TSVFile(history_data_file_name).write(data_list)
    else:
        data_list = TSVFile(DATA_FILE_NAME).read()
        all_timeslots = [AppointmentTimeSlot.from_dict(data) for data in data_list]
    
    report = AvailabilityReport(all_timeslots)
    report.save()
