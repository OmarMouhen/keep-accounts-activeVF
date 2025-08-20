def redirect(self, href_sel=None, **kwargs):
    logger = self.logger
    page = self.tab

    try:
        if href_sel:
            logger.info(f"🔁 Redirecting to element with selector: {href_sel}")
            
            # Wait for the element to be present first
            page.wait_for_selector(href_sel, timeout=10_000, state="attached")
            locator = page.locator(href_sel).first
            
            # Get href with better error handling
            href = locator.get_attribute("href")
            if not href:
                raise ValueError(f"Could not resolve href for selector: {href_sel}")
            
            logger.info(f"🌐 Resolved href: {href}")
            
            # Handle relative vs absolute URLs
            if href.startswith(('http://', 'https://')):
                target_url = href
            else:
                target_url = self.url + href
            
            page.goto(target_url, wait_until="domcontentloaded")
            page.wait_for_selector(href_sel, timeout=10_000, state="visible")
            self.dashboard_url = page.url
            return 0

        elif "button_sel" in kwargs:
            button = kwargs["button_sel"]
            logger.info(f"🔁 Clicking button with selector: {button}")
            
            # Wait for button to be clickable
            page.wait_for_selector(button, timeout=10_000, state="visible")
            page.locator(button).click()
            page.wait_for_load_state("domcontentloaded")
            self.dashboard_url = page.url
            return 0

        elif "url" in kwargs:
            target_url = kwargs["url"]
            logger.info(f"🔁 Redirecting to URL: {target_url}")
            
            # Handle hash replacement more carefully
            if "#" in target_url and "?" not in target_url:
                target_url = target_url.replace("#", "?")
            
            page.goto(target_url, wait_until="domcontentloaded")
            
            # Use wait_for_load_state instead of fixed timeout
            page.wait_for_load_state("networkidle")
            self.dashboard_url = page.url
            return 0

        else:
            raise ValueError("No valid redirect target provided")

    except Exception as e:
        logger.error(f"❌ Redirect failed: {str(e)}")
        # Consider taking a screenshot for debugging
        # page.screenshot(path="redirect_error.png")
        raise
