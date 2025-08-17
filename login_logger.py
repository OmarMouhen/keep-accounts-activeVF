import sys
from urllib import response

sys.dont_write_bytecode = True

import os
import logging
from logging_formatter import CsvFormatter
from time import sleep
import json
import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class LoginLogger:
    def __init__(
        self, base_url, login_url, usr_sel, usr, pwd_sel, pwd, homepage, filename
    ):
        self.url = base_url
        self.login_url = login_url
        self.usr_sel = usr_sel
        self.usr = usr
        self.pwd_sel = pwd_sel
        self.pwd = pwd
        self.homepage = homepage
        self.filename = filename

        self.dashboard_url = None
        self.tab = None

        self.formatter = CsvFormatter(self.filename)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.DuoHandler = logging.StreamHandler()
        self.DuoHandler.setFormatter(self.formatter)
        self.logger.addHandler(self.DuoHandler)

    def one_step_login(self, playwright, button=None):
        logger = self.logger
        logger.info("Launching browser")
        browser = playwright.firefox.launch(args=["--start-maximized"], headless=True)
        page = browser.new_page(no_viewport=True)
        page.route(
            "**/*",
            lambda route: route.abort()
            if (
                route.request.resource_type == "image"
                or route.request.resource_type == "media"
            )
            else route.continue_(),
        )
        page.goto(self.login_url)
        logger.info(f"Retrieving login page '{self.login_url}'")
        page.fill(self.usr_sel, self.usr)
        page.fill(self.pwd_sel, self.pwd)
        if button is not None:
            page.wait_for_selector(button)
            if page.locator(button).is_enabled():
                try:
                    page.click(button)
                    page.keyboard.press("Enter")
                    page.keyboard.press("Enter")
                    logger.info("Logging in")
                except:
                    logger.error("Login button error")
            else:
                page.keyboard.press("Enter")
                page.keyboard.press("Enter")
                logger.info("Logging in")
        else:
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            logger.info("Logging in")

        logger.info("Waiting for redirection or login result...")
        current_url = page.url
        if "blog.mega.io" in current_url:
            logger.error(f"Redirected to unexpected URL: {current_url}")
            raise Exception(f"❌ Unexpected redirect to blog: {current_url}")

        try:
            page.wait_for_selector("div.fm-main", timeout=120_000, state="visible")
            logger.info("✅ Logged in successfully.")
        except PlaywrightTimeoutError:
            logger.error(f"Timeout while waiting for successful login at URL: {page.url}")
            raise Exception("Login failed or timed out.")

        self.tab = page
    def redirect(self, href_sel):
        self.logger.info(f"➡️ Redirecting to element with selector: {href_sel}")
        self.tab.wait_for_selector(href_sel, timeout=10_000)
        self.tab.click(href_sel)
        self.logger.info(f"✅ Redirected successfully.")
