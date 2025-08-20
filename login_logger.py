from __future__ import annotations
from typing import Optional
from urllib.parse import urljoin
from playwright.sync_api import Page

def redirect(
    self,
    href_sel: Optional[str] = None,
    *,
    button_sel: Optional[str] = None,
    url: Optional[str] = None,
    wait_for: Optional[str] = None,      # sélecteur à attendre APRÈS navigation
    timeout: int = 10_000                 # ms
) -> None:
    """
    Redirige vers une nouvelle page selon l’un des modes exclusifs :
    - href_sel : lit l’attribut href d’un élément et navigue
    - button_sel : clique un bouton/élément et attend la navigation
    - url : navigue vers une URL fournie

    Optionnellement, attend un sélecteur `wait_for` sur la page cible.
    Met à jour self.dashboard_url.
    """
    logger = self.logger
    page: Page = self.tab

    # --- validation des paramètres
    supplied = [p is not None for p in (href_sel, button_sel, url)]
    if sum(supplied) != 1:
        raise ValueError("Spécifie exactement un de: href_sel, button_sel, url.")

    if href_sel:
        logger.info(f"🔁 Redirect via href from selector: {href_sel}")
        locator = page.locator(href_sel).first
        href = locator.get_attribute("href")
        logger.info(f"🌐 Resolved href: {href}")
        if not href:
            raise RuntimeError(f"Aucun href trouvé pour {href_sel!r}.")

        target = urljoin(self.url, href)  # gère absolu, relatif, slash, etc.
        logger.info(f"➡️  Navigating to: {target}")

        page.goto(target, wait_until="domcontentloaded", timeout=timeout)

    elif button_sel:
        logger.info(f"🔘 Clicking: {button_sel}")
        with page.expect_navigation(wait_until="domcontentloaded", timeout=timeout):
            page.locator(button_sel).click()

    else:  # url
        target = url
        if not target:
            raise ValueError("Paramètre 'url' vide.")
        logger.info(f"➡️  Navigating to explicit URL: {target}")
        page.goto(target, wait_until="domcontentloaded", timeout=timeout)

    # Attente spécifique après arrivée (facultatif)
    if wait_for:
        logger.info(f"⏳ Waiting for selector on destination: {wait_for}")
        page.wait_for_selector(wait_for, timeout=timeout, state="visible")
    else:
        # Optionnel : s'assurer que la page est stabilisée
        page.wait_for_load_state("networkidle", timeout=timeout)

    self.dashboard_url = page.url
    logger.info(f"✅ Landed at: {self.dashboard_url}")
