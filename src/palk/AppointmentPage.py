import os
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from utils import SECONDS_IN, List, Time, TimeDelta, TimeFormat, mr
from utils.Browser import Browser

from palk._common import log
from palk.AppointmentTimeSlot import AppointmentTimeSlot

URL_BASE = os.path.join(
    'https://eservices.immigration.gov.lk:8443',
    'appointment/pages/reservationApplication.xhtml',
)
WINDOW_WIDTH = 840
WINDOW_HEIGHT = WINDOW_WIDTH * 3

WINDOW_DIM = (WINDOW_WIDTH, WINDOW_HEIGHT)

TIME_FORMAT = TimeFormat('%Y %B %d %I.%M %p')
N_DAYS = 90
HOUR_STRS = ['8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '2 PM']
MAX_THREADS = 4
APPOINTMENT_TYPES = ['Normal Service', 'One Day Service']
LOCATIONS = [
    'HEAD OFFICE - BATTARAMULLA',
]


def custom_sleep():
    time.sleep(4)


class AppointmentPage:
    @staticmethod
    def get_browser():
        browser = Browser()
        browser.set_window_dim(WINDOW_DIM)
        return browser

    def __init__(
        self,
        appointment_type: str,
        location: str,
        time_timeslot: Time,
    ):
        self.appointment_type = appointment_type
        self.location = location
        self.time_timeslot = time_timeslot
        self.browser = None

    @property
    def year_str(self):
        return TimeFormat('%Y').stringify(self.time_timeslot)

    @property
    def month_str(self):
        return TimeFormat('%B').stringify(self.time_timeslot)

    @property
    def day_str(self):
        return TimeFormat('%d').stringify(self.time_timeslot)

    def select_appointment_type(self):
        self.browser.find_element(
            By.XPATH, f'//label[text()="{self.appointment_type}"]'
        ).click()
        custom_sleep()

    def select_location(self):
        tds = self.browser.find_elements(By.TAG_NAME, 'td')
        for i, td in enumerate(tds):
            if td.text == self.location:
                tds[i - 1].click()
                custom_sleep()
                return
        raise Exception(f'Location {self.location} not found')

    def goto_month_page(self):
        MAX_MONTHS = 4
        for i_month in range(MAX_MONTHS):
            elem_month = self.browser.find_element(
                By.CLASS_NAME, 'ui-datepicker-month'
            )
            month_str = elem_month.text
            if month_str == self.month_str:
                break

            elem_next = self.browser.find_element(
                By.CLASS_NAME, 'ui-datepicker-next'
            )
            if 'ui-state-disabled' in elem_next.get_attribute('class'):
                raise Exception('No Data for Month: ' + self.month_str)

            elem_next.click()
            custom_sleep()

    def select_day(self):
        try:
            a = self.browser.find_element(
                By.XPATH, f'//a[text()="{self.day_str}"]'
            )
            a.click()
            custom_sleep()
        except NoSuchElementException:
            raise Exception(
                f'No Data for Day: {self.month_str}/{self.day_str}'
            )

    def select_hour(self, hour_str: str):
        try:
            span = self.browser.find_element(
                By.XPATH, f'//span[text()="{hour_str}"]'
            )
            span.click()
            custom_sleep()
        except NoSuchElementException:
            raise Exception('No Data for Hour: ' + hour_str)

    def parse_qtr_hours(
        self,
    ) -> list:
        N_BUTTONS_QTR_HOUR = 4
        appointment_timeslots = []
        n_is_available = 0
        for i_button_qtr_hour in range(N_BUTTONS_QTR_HOUR):
            id = f'reservation:j_idt226:{i_button_qtr_hour}' + ':j_idt227'
            button_qtr_hour = self.browser.find_element(By.ID, id)
            is_available = 'old' not in button_qtr_hour.get_attribute('class')
            if is_available:
                n_is_available += 1
            qtr_hour_str = button_qtr_hour.text
            qtr_hour_start_str = qtr_hour_str[:5] + ' ' + qtr_hour_str[-2:]
            time_str_raw = (
                f'{self.year_str} {self.month_str} '
                + f'{self.day_str} {qtr_hour_start_str}'
            )
            t = TIME_FORMAT.parse(time_str_raw)

            appointment_timeslot = AppointmentTimeSlot(
                appointment_type=self.appointment_type,
                location=self.location,
                ut=t.ut,
                is_available=is_available,
            )
            log.debug(appointment_timeslot.to_dict)
            appointment_timeslots.append(appointment_timeslot)

        return appointment_timeslots

    def get_timeslots(self):
        self.browser = AppointmentPage.get_browser()
        self.browser.open(URL_BASE)

        self.select_appointment_type()
        self.select_location()

        all_appointment_timeslots = []
        try:
            self.goto_month_page()
            self.select_day()
            for hour_str in HOUR_STRS:
                self.select_hour(hour_str)
                all_appointment_timeslots += self.parse_qtr_hours()
        except Exception as e:
            log.warning(e)

        self.browser.quit()

        return all_appointment_timeslots

    @staticmethod
    def get_all_timeslots(is_test_mode=False) -> list:
        time_now = Time()
        all_appointment_timeslots = []
        pages = []
        for appointment_type in APPOINTMENT_TYPES:
            for location in LOCATIONS:
                for i_day in range(N_DAYS):
                    time_timeslot = time_now + TimeDelta(
                        i_day * SECONDS_IN.DAY
                    )
                    page = AppointmentPage(
                        appointment_type=appointment_type,
                        location=location,
                        time_timeslot=time_timeslot,
                    )
                    pages.append(page)

        if is_test_mode:
            import random
            N_TEST_PAGES = 10
            log.warning(f'{is_test_mode=}. Picking {N_TEST_PAGES} random pages.')
            random.shuffle(pages)
            pages = pages[:N_TEST_PAGES]

        n_pages = len(pages)
        log.info(f'Scraping {n_pages} pages.')

        def inner(page=page):
            try:
                return page.get_timeslots()
            except Exception as e:
                log.warning(e)
                return []

        all_appointment_timeslots_list = mr.map_parallel(
            lambda page: inner(page=page),
            pages,
            max_threads=MAX_THREADS,
        )
        all_appointment_timeslots = List(
            all_appointment_timeslots_list
        ).flatten()
        return all_appointment_timeslots


def test_appointment_page():
    time_timeslot = Time() + TimeDelta(90 * SECONDS_IN.DAY)
    page = AppointmentPage(
        appointment_type="Normal Service",
        location="HEAD OFFICE - BATTARAMULLA",
        time_timeslot=time_timeslot,
    )
    print(page.get_timeslots())


def test_static():
    print(AppointmentPage.get_all_timeslots())


if __name__ == '__main__':
    test_appointment_page()
    # test_static()
