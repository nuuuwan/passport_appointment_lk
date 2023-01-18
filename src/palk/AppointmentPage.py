import os
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from utils import TIME_FORMAT_TIME, Time, TimeFormat
from utils.Browser import Browser

from palk._common import log
from palk.AppointmentTimeSlot import AppointmentTimeSlot

URL_BASE = os.path.join(
    'https://eservices.immigration.gov.lk:8443',
    'appointment/pages/reservationApplication.xhtml',
)
WINDOW_WIDTH = 840
WINDOW_HEIGHT = WINDOW_WIDTH * 3
TIME_FORMAT = TimeFormat('%Y %B %d %I.%M %p')


class AppointmentPage:
    @staticmethod
    def get_driver():
        browser = Browser()
        browser.browser.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        browser.open(URL_BASE)
        return browser.browser

    @staticmethod
    def sleep():
        T_SLEEP = 2
        log.debug(f'😴 Sleeping for {T_SLEEP}s')
        time.sleep(T_SLEEP)

    def __init__(
        self, appointment_type: str, location: str, timeslot_time: Time
    ):
        self.application_type = appointment_type
        self.location = location
        self.timeslot_time = timeslot_time

        self.driver = None

    @property
    def year_str(self):
        return TimeFormat('%Y').stringify(self.timeslot_time)

    @property
    def month_str(self):
        return TimeFormat('%B').stringify(self.timeslot_time)

    @property
    def day_str(self):
        return TimeFormat('%d').stringify(self.timeslot_time)

    @property
    def hour_str(self):
        return TimeFormat('%-I %p').stringify(self.timeslot_time)

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def select_application_type(self):
        log.debug(f'select_application_type: {self.application_type}')
        self.find_element(
            By.XPATH, f'//label[text()="{self.application_type}"]'
        ).click()
        AppointmentPage.sleep()

    def select_location(self):
        log.debug(f'select_location: {self.location}')
        tds = self.find_elements(By.TAG_NAME, 'td')
        for i, td in enumerate(tds):
            if td.text == self.location:
                tds[i - 1].click()
                AppointmentPage.sleep()
                return
        raise Exception(f'Location {self.location} not found')

    def goto_month_page(self):
        log.debug(f'goto_month_page: {self.month_str}')
        MAX_MONTHS = 4
        for i_month in range(MAX_MONTHS):
            elem_month = self.find_element(
                By.CLASS_NAME, 'ui-datepicker-month'
            )
            month_str = elem_month.text
            if month_str == self.month_str:
                break

            elem_next = self.find_element(By.CLASS_NAME, 'ui-datepicker-next')
            if 'ui-state-disabled' in elem_next.get_attribute('class'):
                raise Exception('No Data for Month: ' + self.month_str)

            elem_next.click()
            AppointmentPage.sleep()

    def select_day(self):
        log.debug(f'select_day: {self.day_str}')
        try:
            a = self.find_element(By.XPATH, f'//a[text()="{self.day_str}"]')
            a.click()
            self.sleep()
        except NoSuchElementException:
            raise Exception('No Data for Day: ' + self.day_str)

    def select_hour(self):
        log.debug(f'select_hour: {self.hour_str}')
        try:
            span = self.find_element(
                By.XPATH, f'//span[text()="{self.hour_str}"]'
            )
            span.click()
            self.sleep()
        except NoSuchElementException:
            raise Exception('No Data for Hour: ' + self.hour_str)

    def get_available_timeslots(self) -> list:
        self.driver = AppointmentPage.get_driver()
        self.select_application_type()
        self.select_location()
        self.goto_month_page()
        self.select_day()
        self.select_hour()

        N_BUTTONS_QTR_HOUR = 4
        appointment_timeslots = []
        for i_button_qtr_hour in range(N_BUTTONS_QTR_HOUR):
            log.debug(f'i_button_qtr_hour: {i_button_qtr_hour}')
            id = f'reservation:j_idt226:{i_button_qtr_hour}' + ':j_idt227'
            button_qtr_hour = self.find_element(By.ID, id)
            is_available = 'old' not in button_qtr_hour.get_attribute('class')
            qtr_hour_str = button_qtr_hour.text
            qtr_hour_start_str = qtr_hour_str[:5] + ' ' + qtr_hour_str[-2:]
            time_str_raw = (
                f'{self.year_str} {self.month_str} '
                + f'{self.day_str} {qtr_hour_start_str}'
            )
            t = TIME_FORMAT.parse(time_str_raw)

            appointment_timeslot = AppointmentTimeSlot(
                appointment_type=self.application_type,
                location=self.location,
                ut=t.ut,
                is_available=is_available,
            )
            log.debug(appointment_timeslot.to_dict)
            appointment_timeslots.append(appointment_timeslot)
        self.driver.close()
        self.driver.quit()
        return appointment_timeslots


if __name__ == '__main__':
    t = TIME_FORMAT_TIME.parse('2022-01-19 8:00:00 +0530')
    page = AppointmentPage('One Day Service', 'HEAD OFFICE - BATTARAMULLA', t)
    for application_timeslot in page.get_available_timeslots():
        print(application_timeslot)
