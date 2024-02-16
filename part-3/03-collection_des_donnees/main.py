import webbrowser
from datetime import datetime
from dateutil.relativedelta import relativedelta

from playwright.sync_api import sync_playwright

from price import get_average_price

SBR_WS_CDP = ""  # L'URL de votre Scraping Browser


def open_debug_view(page):
    """Open the Bright Data Debug View"""

    client = page.context.new_cdp_session(page)
    frame_tree = client.send('Page.getFrameTree', {})
    frame_id = frame_tree['frameTree']['frame']['id']
    inspect = client.send('Page.inspect', {'frameId': frame_id})
    inspect_url = inspect['url']
    webbrowser.open(inspect_url)


def route_intercept(route):
    if route.request.resource_type == "image":
        return route.abort()
    return route.continue_()


def run(pw, city: str, bright_data: bool = False, headless: bool = False):
    print("Connecting to Scraping Browser")
    if bright_data:
        browser = pw.chromium.connect_over_cdp(SBR_WS_CDP)
    else:
        browser = pw.chromium.launch(headless=headless)

    context = browser.new_context()
    context.set_default_timeout(60000)

    page = context.new_page()
    # page.route("**/*", route_intercept)

    if bright_data and not headless:
        open_debug_view(page)

    url = f"https://www.airbnb.fr/"

    page.goto(url)
    page.get_by_text("Continuer sans accepter").click()
    page.get_by_role("button", name="Explorer les logements").click()
    page.get_by_test_id("structured-search-input-field-query").click()
    page.get_by_test_id("structured-search-input-field-query").fill(city)
    page.get_by_test_id("option-0").click()
    page.get_by_test_id("expanded-searchbar-dates-months-tab").click()
    page.locator(".d1u68d5p").first.click()
    page.get_by_test_id("structured-search-input-field-guests-button").click()
    page.get_by_test_id("stepper-adults-increase-button").click()
    page.get_by_test_id("structured-search-input-search-button").click()
    today = datetime.today()

    for i in range(2, 14):
        next_month = today + relativedelta(months=i, day=1)
        next_month_str = next_month.strftime("%d/%m/%Y")

        page.wait_for_timeout(2000)

        html_content = page.content()
        average_price = get_average_price(html=html_content)
        print(f"Average price for date {next_month_str} is {average_price}")

        page.get_by_test_id("little-search").click()
        page.get_by_role("button").filter(has_text="Modifier").click()
        page.wait_for_timeout(500)
        page.get_by_test_id(f"calendar-day-{next_month_str}").last.click()
        page.locator("button:has-text('Appliquer')").click()
        page.get_by_test_id("structured-search-input-search-button").click()
        page.wait_for_timeout(400)

    browser.close()


if __name__ == '__main__':
    with sync_playwright() as playwright:
        run(pw=playwright,
            city="Porto",
            bright_data=True,
            headless=False)
