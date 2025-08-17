
def redirect(self, href_sel=None, **kwargs):
    logger = self.logger
    page = self.tab

    if href_sel:
        logger.info(f"🔁 Redirecting to element with selector: {href_sel}")
        locator = self.tab.locator(href_sel).first
        href = locator.get_attribute("href")
        logger.info(f"🌐 Resolved href: {href}")
        if href is None:
            raise Exception("Could not resolve href for the selector.")
        page.goto(self.url + href)
        page.wait_for_selector(href_sel, timeout=10_000, state="visible")
        self.dashboard_url = page.url
        return 0

    elif "button_sel" in kwargs:
        button = kwargs.get("button_sel")
        page.locator(button).click()
        page.wait_for_load_state("domcontentloaded")
        self.dashboard_url = page.url
        return 0

    elif "url" in kwargs:
        self.dashboard_url = kwargs.get("url")
        if "#" in self.dashboard_url:
            self.dashboard_url = self.dashboard_url.replace("#", "?")
        page.goto(self.dashboard_url)
        page.wait_for_timeout(2529)
