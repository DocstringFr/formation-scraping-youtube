import webbrowser
from playwright.sync_api import sync_playwright

SBR_WS_CDP = ""  # L'URL de votre Scraping Browser


def open_debug_view(page):
    client = page.context.new_cdp_session(page)
    frame_tree = client.send('Page.getFrameTree', {})
    frame_id = frame_tree['frameTree']['frame']['id']
    inspect = client.send('Page.inspect', {'frameId': frame_id})
    inspect_url = inspect['url']
    print('Inspect session at', inspect_url)
    webbrowser.open(inspect_url)


def route_intercept(route):
    if route.request.resource_type == "image":
        return route.abort()
    return route.continue_()


def run(pw, bright_data=False, headless=False):
    print('Connecting to Scraping Browser...')
    if bright_data:
        browser = pw.chromium.connect_over_cdp(SBR_WS_CDP)
    else:
        browser = pw.chromium.launch(headless=headless)

    try:
        context = browser.new_context()
        context.set_default_timeout(60000)
        page = context.new_page()
        page.route("**/*", route_intercept)

        if bright_data and not headless:
            open_debug_view(page)

        url = f"https://www.airbnb.fr/s/Rio-de-Janeiro--Rio-de-Janeiro--Br%C3%A9sil/homes?tab_id=home_tab&monthly_start_date=2024-01-01&monthly_length=3&price_filter_input_type=0&channel=EXPLORE&query=Rio%20de%20Janeiro,%20Br%C3%A9sil&date_picker_type=flexible_dates&flexible_trip_dates%5B%5D=january&flexible_trip_lengths%5B%5D=one_month&adults=1&source=structured_search_input_header&search_type=autocomplete_click&price_filter_num_nights=28&place_id=ChIJW6AIkVXemwARTtIvZ2xC3FA"
        page.goto(url)
        page_number = 1
        while True:
            print(f"Scraping page {page_number}...")
            next_page = page.locator('a[aria-label="Suivant"]')
            if next_page.get_attribute('aria-disabled') == 'true':
                break
            next_page.click()
            page_number += 1
    finally:
        browser.close()

    return None


def main(bright_data=False, headless=False):
    with sync_playwright() as playwright:
        run(pw=playwright,
            bright_data=bright_data,
            headless=headless)


if __name__ == '__main__':
    main(bright_data=True,
         headless=False)
