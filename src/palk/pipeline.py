from utils import TIME_FORMAT_TIME_ID, Time, TSVFile

from palk._common import log
from palk.AppointmentPage import AppointmentPage
from palk.AvailabilityReport import AvailabilityReport

N_DAYS = 60
FORCE_SCRAPE = True

if __name__ == '__main__':
    all_timeslots = AppointmentPage.get_all_timeslots()
    data_list = [x.to_dict for x in all_timeslots]

    if data_list:

        latest_file_name = '/tmp/palk.latest.tsv'
        TSVFile(latest_file_name).write(data_list)
        log.info(f'Wrote data to "{latest_file_name}".')

        time_now = Time()
        time_id = TIME_FORMAT_TIME_ID.stringify(time_now)
        history_file_name = f'/tmp/palk.{time_id}.tsv'
        TSVFile(history_file_name).write(data_list)
        log.info(f'Wrote data to "{history_file_name}".')

    report = AvailabilityReport(all_timeslots)
    report.save()
