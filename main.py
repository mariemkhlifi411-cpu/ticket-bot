from playwright.sync_api import sync_playwright
import time

URL = "https://siga.marcacaodeatendimento.pt/"
EMAIL = "mariem.khlifi21@gmail.com"

TARGET_LOCATIONS = [
    "Loja de Cidadão Saldanha",
    "Loja de Cidadão Laranjeiras",
]


def select_by_text(page, select_id, text):
    page.evaluate(
        """
        ({ selectId, text }) => {
            const select = document.querySelector(`#${selectId}`);
            const option = [...select.options].find(o => o.text.trim() === text);
            if (!option) throw new Error(`Option not found: ${text}`);
            select.value = option.value;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            if (window.$) {
                window.$(`#${selectId}`).selectpicker('refresh');
            }
        }
        """,
        {"selectId": select_id, "text": text},
    )
    time.sleep(2)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1000})

        print("Opening SIGA...")
        page.goto(URL, wait_until="networkidle", timeout=60000)

        print("Opening Consultar filas de espera...")
        page.get_by_role("link", name="Consultar filas de espera").click(timeout=30000)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        print("Selecting Distrito...")
        select_by_text(page, "IdDistrito", "Lisboa")

        print("Selecting Entidade...")
        select_by_text(page, "IdEntidade", "Instituto da Segurança Social, IP")

        print("Selecting Senha...")
        select_by_text(page, "IdSenha", "Geral")

        print("Searching...")
        page.get_by_role("button", name="Pesquisar").click(timeout=30000)
        time.sleep(6)

        found = False

        for page_number in range(1, 4):
            print(f"Checking result page {page_number}...")

            rows = page.locator("table tbody tr")
            count = rows.count()

            for i in range(count):
                row = rows.nth(i)
                text = row.inner_text()

                for location in TARGET_LOCATIONS:
                    if location in text and "Tirar Senha" in text:
                        print(f"FOUND: {location}")

                        row.get_by_text("Tirar Senha", exact=True).click()
                        time.sleep(2)

                        page.locator("input").last.fill(EMAIL)
                        page.get_by_role("button", name="Continuar").click()

                        print("Ticket request submitted.")
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
