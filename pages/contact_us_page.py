from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class ContactUsPage(BasePage):
   
    def __init__(self, page: Page):
        super().__init__(page)
        self.contact_us_button = page.locator("a:has-text('Contact Us')")
        self.name_field = page.locator("[data-qa='name1']")
        self.email_field = page.locator("[data-qa='email']")
        self.subject_field = page.locator("[data-qa='subject']")
        self.message_field = page.locator("[data-qa='message']")
        self.file_input = page.locator("input[name='upload_file']")
        self.submit_button = page.locator("[data-qa='submit-button']")

    def open_contact_us(self) -> None:
        self.click(self.contact_us_button, name="contact us button")
        self.page.wait_for_url("**/contact_us")
        self.page.wait_for_load_state("load")
        self.name_field.wait_for(state="visible")

    def fill_contact_form(self, name: str, email: str, subject: str, message: str) -> None:
        self.fill(self.name_field, name, name="name field")
        self.fill(self.email_field, email, name="email field")
        self.fill(self.subject_field, subject, name="subject field")
        self.fill(self.message_field, message, name="message field")

    def attach_file(self, file_path: str) -> None:
        self.set_input_files(self.file_input, [file_path])

    def submit_form(self) -> None:
        self.click(self.submit_button, name="submit button") 

    def accept_alert(self) -> None:
        self.page.on("dialog", lambda dialog: dialog.accept())

    def get_success_message(self) -> str:
        success_message_locator = self.page.locator("[class='status alert alert-success']")
        success_message_locator.wait_for(state="visible")
        return self.text_of(success_message_locator, name="success message")           