import math
import time
import json
import pprint

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from main.models import SofaType, Sofa, Color
from .locators import SingleSofaLocators, ManySofaLocators, SofaTypeListLocators
from .url_data import URLS


def chrome_webdriver_config():
    CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome()

    webdriver_config = {
        "executable_path": CHROMEDRIVER_PATH,
        "chrome_options": chrome_options,
    }

    return webdriver_config


class Command(BaseCommand):
    help = "Scrape IKEA for sofa data"

    ITEMS_PER_PAGE = 24

    def __init__(self, *args, **kwargs):
        config = chrome_webdriver_config()
        self.driver = webdriver.Chrome(**config)

        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("dump_filename", nargs="+", type=str)

    def handle(self, *args, **options):
        self.dump_filename = options["dump_filename"][0] or "items.json"
        self.driver.implicitly_wait(3)
        self.clean_database()

        current_url = URLS[0]

        try:
            scraped_items = None
            print(self.style.MIGRATE_HEADING(f"Scraping items..."))

            for u in tqdm(URLS):
                current_url = u
                scraped_items = self.scrape_pages(url=u)

            if scraped_items:
                number_of_items = len(scraped_items)
                with open(self.dump_filename, "w") as f:
                    json.dump(scraped_items, f)

                    pp = pprint.PrettyPrinter()
                    pp.pprint(scraped_items)
                    print(
                        self.style.SUCCESS(
                            f"Dumped {number_of_items} items to {self.dump_filename}"
                        )
                    )

        except Exception as e:
            print(f"{self.style.ERROR(e)}\n")

        finally:
            self.driver.close()

    def scrape_pages(self, url=URLS[0]):
        self.driver.get(url)

        number_of_items = self.driver.find_element(
            *SofaTypeListLocators.NUMBER_OF_ITEMS
        ).text

        total_pages = math.ceil(int(number_of_items) / self.ITEMS_PER_PAGE)
        self.driver.get(url + f"&page={total_pages}")

        time.sleep(3)

        name_elements = self.driver.find_elements(*ManySofaLocators.NAME)
        type_elements = self.driver.find_elements(*ManySofaLocators.TYPE)
        image_elements = self.driver.find_elements(*ManySofaLocators.IMAGE)

        names = [i.text for i in name_elements]
        types = [i.text for i in type_elements]
        image_urls = [i.get_attribute("src") for i in image_elements]

        for i, name in enumerate(names):
            sofa_type, created = SofaType.objects.get_or_create(description=types[i])
            sofa, created = Sofa.objects.get_or_create(
                name=name, image_url=image_urls[i], type=sofa_type
            )
            sofa.save()

        return [s.as_dict() for s in Sofa.objects.all()]

    def clean_database(self):
        print(self.style.MIGRATE_HEADING(f"Cleaning database..."))
        SofaType.objects.all().delete()
        Sofa.objects.all().delete()
        Color.objects.all().delete()
