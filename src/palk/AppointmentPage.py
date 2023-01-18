import os
import time

from selenium.webdriver.common.by import By
from utils import Time, TimeFormat
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
    def __init__(self):
        self.browser = Browser()
        self.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.browser.open(URL_BASE)

    def downloadScreenshot(self, image_file_name: str):
        self.driver.save_screenshot(image_file_name)

    @property
    def year(self):
        return TimeFormat('%Y').stringify(Time())

    @property
    def driver(self):
        return self.browser.browser

    @property
    def elem_table_date_picker(self):
        return self.driver.find_element(
            By.CLASS_NAME, 'ui-datepicker-calendar'
        )

    def sleep(self):
        T_SLEEP = 2
        log.debug(f'Sleeping for {T_SLEEP}s...')
        time.sleep(T_SLEEP)

    def set_application_type(self, application_type: str):
        self.application_type = application_type

        self.driver.find_element(
            By.XPATH, f'//label[text()="{application_type}"]'
        ).click()
        self.sleep()

    def set_location(self, location: str):
        self.location = location

        tds = self.driver.find_elements(By.TAG_NAME, 'td')
        for i, td in enumerate(tds):
            if td.text == location:
                tds[i - 1].click()
                self.sleep()
                return
        raise Exception(f'Preferred location {location} not found')

    def get_available_timeslots(self):
        assert self.application_type and self.location
        appointment_timeslots = []

        while True:
            elem_month = self.driver.find_element(
                By.CLASS_NAME, 'ui-datepicker-month'
            )
            month_str = elem_month.text
            for td in self.elem_table_date_picker.find_elements(
                By.TAG_NAME, 'td'
            ):
                if 'disabled' in td.get_attribute('class'):
                    continue

                date_str = td.text
                td.click()
                self.sleep()

                table_morning = self.driver.find_element(
                    By.ID, 'reservation:j_idt207'
                )
                table_afternoon = self.driver.find_element(
                    By.ID, 'reservation:j_idt214'
                )
                buttons = table_morning.find_elements(
                    By.TAG_NAME, 'button'
                ) + table_afternoon.find_elements(By.TAG_NAME, 'button')

                for button in buttons:
                    button.text
                    button.click()
                    self.sleep()
                    table_sessions = self.driver.find_element(
                        By.ID, 'reservation:j_idt222'
                    )
                    for button in table_sessions.find_elements(
                        By.TAG_NAME, 'button'
                    ):
                        is_available = 'old' not in button.get_attribute(
                            'class'
                        )
                        qtr_hour_str = button.text
                        qtr_hour_start_str = (
                            qtr_hour_str[:5] + ' ' + qtr_hour_str[-2:]
                        )
                        time_str_raw = (
                            f'{self.year} {month_str} '
                            + f'{date_str} {qtr_hour_start_str}'
                        )
                        time = TIME_FORMAT.parse(time_str_raw)

                        appointment_timeslot = AppointmentTimeSlot(
                            appointment_type=self.application_type,
                            location=self.location,
                            ut=time.ut,
                            is_available=is_available,
                        )
                        appointment_timeslots.append(appointment_timeslot)
                    break
                break

            elem_next = self.driver.find_element(
                By.CLASS_NAME, 'ui-datepicker-next'
            )
            if 'ui-state-disabled' in elem_next.get_attribute('class'):
                break
            elem_next.click()
            self.sleep()
        return appointment_timeslots
