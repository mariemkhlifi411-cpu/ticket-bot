from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import time

URL = "https://siga.marcacaodeatendimento.pt/"
EMAIL = "mariem.khlifi21@gmail.com"

TARGET_LOCATIONS = [
    "Loja de Cidadão Saldanha",
    "Loja de Cidadão Laranjeiras",
]

SKIP_LOCATIONS = [
    "Loja de Cidadão Mafra",
    "Loja de Cidadão Cascais",
]


def select_option(page, label_text, option_text):
    field = page.get_by_text(label_text, exact=False).locator("..").locator("input, select, div").first
    page.get_by_text(label_text, exact=False).click()
    time.sleep(1)
    page.get_by_text(option_text, exact=True).click()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1000})

        print("Opening SIGA...")
        page.goto(URL, wait_until="networkidle", timeout=60000)

        try:
            page.get_by_text("Concordo", exact=True).click(timeout=5000)
        except:
            pass

        print("Opening Consultar filas de espera...")
        page.get_by_role("link", name="Consultar filas de espera").click(timeout=30000)
        
        page.wait_for_load_state("networkidle")

        print("Selecting Distrito...")
        page.get_by_label("Distrito").click()
        page.get_by_text("Lisbon", exact=True).click()

        print("Selecting Entidade...")
        page.get_by_label("Entidade").click()
        page.get_by_text("Instituto da Segurança Social, IP", exact=True).click()

        print("Selecting Senha...")
        page.get_by_label("Senha").click()
        page.get_by_text("Geral", exact=True).click()

        print("Searching...")
        page.get_by_text("Pesquisar", exact=True).click()
        page.wait_for_load_state("networkidle")
        time.sleep(5)

        found = False

        for page_number in range(1, 4):
            print(f"Checking page {page_number}...")

            rows = page.locator("table tbody tr")
            count = rows.count()

            for i in range(count):
                row = rows.nth(i)
                row_text = row.inner_text()

                if any(skip in row_text for skip in SKIP_LOCATIONS):
                    continue

                for location in TARGET_LOCATIONS:
                    if location in row_text and "Tirar Senha" in row_text:
                        print(f"FOUND TICKET: {location}")

                        row.get_by_text("Tirar Senha", exact=True).click()
                        time.sleep(2)

                        page.locator("input[type='email'], input").last.fill(EMAIL)
                        page.get_by_text("Continuar", exact=True).click()

                        print("Ticket requested successfully.")
                        found = True
                        break

                if found:
                    break

            if found:
                break

            try:
                page.get_by_text(str(page_number + 1), exact=True).click(timeout=5000)
                time.sleep(4)
            except:
                break

        if not found:
            print("No ticket available for Saldanha or Laranjeiras right now.")

        browser.close()


if __name__ == "__main__":
    main()
