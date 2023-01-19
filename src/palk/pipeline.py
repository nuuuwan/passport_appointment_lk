import os

from utils import TIME_FORMAT_TIME_ID, Git, Time, TSVFile

from palk._common import DIR_REPO, GIT_REPO_URL, REPO_BRANCH_DATA, log
from palk.AppointmentPage import AppointmentPage
from palk.AvailabilityReport import AvailabilityReport
from palk.SummaryReport import SummaryReport

N_DAYS = 60
FORCE_SCRAPE = True

def run(is_test_mode):
    git = Git(GIT_REPO_URL)
    git.clone(DIR_REPO, force=True)
    git.checkout(REPO_BRANCH_DATA)

    all_timeslots = AppointmentPage.get_all_timeslots(is_test_mode)
    data_list = [x.to_dict for x in all_timeslots]    

    if data_list:

        latest_file_name = os.path.join(DIR_REPO, 'palk.latest.tsv')
        TSVFile(latest_file_name).write(data_list)
        log.info(f'Wrote data to "{latest_file_name}".')

        time_now = Time()
        time_id = TIME_FORMAT_TIME_ID.stringify(time_now)
        history_file_name = os.path.join(DIR_REPO, f'palk.{time_id}.tsv')
        TSVFile(history_file_name).write(data_list)
        log.info(f'Wrote data to "{history_file_name}".')

    availability_report = AvailabilityReport(all_timeslots)
    availability_report.save()

    summary_report = SummaryReport()
    summary_report.save()

if __name__ == '__main__':
    run(is_test_mode=False)
