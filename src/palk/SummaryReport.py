import math
import os
from dataclasses import dataclass

import matplotlib.pyplot as plt
from utils import (SECONDS_IN, TIME_FORMAT_TIME, Directory, File, Log, Time,
                   TimeFormat, TSVFile)

from palk._common import DIR_REPO
from palk.AppointmentPage import URL_BASE
from palk.AppointmentTimeSlot import AppointmentTimeSlot

log = Log('SummaryReport')


class SummaryDataWaitTimeChart:
    PNG_FILE_NAME = 'summary.wait_time_chart.png'
    PNG_FILE_PATH = os.path.join(DIR_REPO, PNG_FILE_NAME)

    def __init__(self, data_list):
        self.data_list = data_list

    def save(self):
        x = [
            TimeFormat('%Y-%m-%d %H:%M').stringify(Time(data.ut))
            for data in self.data_list
        ]
        y = [data.ho_ods_wait_days for data in self.data_list]

        plt.xticks(rotation=45)
        plt.plot(x, y)
        # show every other x axis label
        labels = plt.gca().xaxis.get_ticklabels()
        for label in labels:
            label.set_visible(False)
        N_DISPLAY_LABELS = 7
        for j in range(0, N_DISPLAY_LABELS):
            i = int(j * len(labels) / N_DISPLAY_LABELS)
            labels[i].set_visible(True)

        plt.title('Wait Times (in Days) for One Day Service at Head Office')

        plt.tight_layout()
        plt.savefig(self.PNG_FILE_PATH)
        log.info(f'Saved SummaryDataWaitTimeChart to {self.PNG_FILE_PATH}')
        return self.PNG_FILE_NAME


@dataclass
class SummaryData:
    ut: int
    ho_ods_wait_days: int
    ho_ods_total_free_time_slots: int

    @staticmethod
    def from_data_file(file):
        data_list = TSVFile(file.path).read()
        all_timeslots = [
            AppointmentTimeSlot.from_dict(data) for data in data_list
        ]
        ho_ods_timeslots = [
            timeslot
            for timeslot in all_timeslots
            if timeslot.appointment_type == 'One Day Service'
            and timeslot.location == 'HEAD OFFICE - BATTARAMULLA'
        ]
        ut = TimeFormat('%Y%m%d%H%M%S%Z').parse(file.name[5:-4]).ut
        ut_now = Time().ut

        ho_ods_wait_s = None
        ho_ods_total_free_time_slots = 0
        for timeslot in ho_ods_timeslots:
            if not timeslot.is_available:
                continue
            ho_ods_total_free_time_slots += 1
            wait_s = timeslot.ut - ut_now

            if not ho_ods_wait_s or ho_ods_wait_s > wait_s:
                ho_ods_wait_s = wait_s

        ho_ods_wait_days = math.ceil(ho_ods_wait_s / SECONDS_IN.DAY)

        return SummaryData(
            ut=ut,
            ho_ods_wait_days=ho_ods_wait_days,
            ho_ods_total_free_time_slots=ho_ods_total_free_time_slots,
        )


class SummaryReport:
    MD_FILE_PATH = os.path.join(DIR_REPO, 'summary.md')

    @staticmethod
    def isDataFile(file_or_dir):
        return file_or_dir.name.startswith('palk.20')

    @property
    def header_lines(self):
        time_str = TIME_FORMAT_TIME.stringify(Time())
        return [
            '# Summary Report',
            'Of the data from the Passport Application Reservation System'
            + ' of the Sri Lanka Department of Immigration and Emigration.',
            f'*As of {time_str}*',
        ]

    def get_summary_data(self):
        data_list = []
        for child in Directory(DIR_REPO).children:
            if not SummaryReport.isDataFile(child):
                continue
            data = SummaryData.from_data_file(child)
            data_list.append(data)
        return sorted(data_list, key=lambda data: data.ut)

    @property
    def footer_lines(self):
        return [
            'Data Source:'
            + f' [Passport Application Reservation System]({URL_BASE})',
        ]

    @property
    def body_lines(self):
        data_list = self.get_summary_data()
        wait_time_chart_png_file_path = SummaryDataWaitTimeChart(
            data_list
        ).save()
        return [f'![Wait Time Chart]({wait_time_chart_png_file_path})']

    @property
    def lines(self):

        return self.header_lines + self.body_lines + self.footer_lines

    def save(self):
        content = '\n\n'.join(self.lines)
        File(self.MD_FILE_PATH).write(content)
        log.info(f'Saved SummaryReport to {self.MD_FILE_PATH}')


if __name__ == '__main__':
    SummaryReport().save()
