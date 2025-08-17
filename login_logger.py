import sys
sys.dont_write_bytecode = True

import os
import logging
from logging_formatter import CsvFormatter
from time import sleep
import json
import re


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
                    logger.info("Logging in with button")
                except:
                    logger.error("Login button error")
            else:
                page.keyboard.press("Enter")
                logger.info("Logging in without button (disabled)")
        else:
            page.keyboard.press("Enter")
            logger.info("Logging in without button (no selector provided)")

        page.wait_for_timeout(4000)
        current_url = page.url
        if "blog.mega.io" in current_url:
            logger.error(f"❌ Unexpected redirect to: {current_url}")
            try:
                page.screenshot(path="login-failure.png")
                logger.info("📸 Screenshot saved to 'login-failure.png'")
            except:
                logger.warning("Screenshot capture failed.")
            raise Exception("Login failed or blocked (redirected to blog)")

        try:
            page.wait_for_selector("div.fm-main", timeout=120_000, state="visible")
            logger.info("✅ Successfully logged into MEGA dashboard.")
        except:
            logger.error("❌ Login possibly failed. 'div.fm-main' did not become visible.")
            try:
                page.screenshot(path="login-timeout.png")
                logger.info("📸 Screenshot saved to 'login-timeout.png'")
            except:
                logger.warning("Screenshot capture failed.")
            raise Exception("Login failed or timed out.")

        self.tab = page
