import csv
import json
import os
import time

from django.core.management.base import BaseCommand, CommandError
from ezscrape.scraping import scraper
from ezscrape.scraping.core import ScrapeConfig
from ezscrape.scraping.core import ScrapeStatus

from inventory.models import Part


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parts_per_scrape = 100

    def add_arguments(self, parser):
        parser.add_argument('rebrickabe_api_key', type=str)
        parser.add_argument('json_file_path', type=str)
        parser.add_argument('-p', '--parts_from_csv', type=str, help='Loads the Parts from a csv instead of the DB', )

    def handle(self, *args, **options):
        rebrickabe_api_key = options['rebrickabe_api_key']
        json_file_path = options['json_file_path']
        parts_csv_path = options['parts_from_csv']

        self.scrape_rebrickable_parts(rebrickabe_api_key, json_file_path, parts_csv_path)

    def scrape_rebrickable_parts(self, api_key, json_file_path, part_csv_path):
        self.stdout.write(F'Scraping Rebrickable Parts')

        # Get the data to scrape
        part_nums, data_dic = self._load_scrape_data(json_file_path, part_csv_path)

        # Get the list to scrape next
        scrape_list, part_nums = self._get_scrape_list(part_nums, self.parts_per_scrape)
        while scrape_list:
            # Do the scraping
            scrape_data = self._scrape(self._form_scrape_url(scrape_list, api_key))
            if scrape_data:
                data_dic = self._process_scrape_result(scrape_data, data_dic)
                self._save_scrape(json_file_path, data_dic, part_nums)
            else:
                self._save_scrape(json_file_path, data_dic, part_nums + scrape_list)

            # Get the next Part Nums to scrape
            scrape_list, part_nums = self._get_scrape_list(part_nums, self.parts_per_scrape)

            # delay between scrape attempts
            time.sleep(2)

        self.stdout.write(F'Scraping Complete')

    @staticmethod
    def _get_part_nums_from_rebrickable_csv(part_csv_path):
        part_num_list = []
        with open(part_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                part_num_list.append(row['part_num'])

        return part_num_list

    @staticmethod
    def _get_scrape_list(part_nums, count):
        scrape_list = []
        leftover_part_nums = []

        if len(part_nums) > count:
            scrape_list = part_nums[:count]
            leftover_part_nums = part_nums[count:]
        else:
            scrape_list = part_nums

        return (scrape_list, leftover_part_nums)

    @staticmethod
    def _form_scrape_url(part_nums, api_key):
        part_list_str = ','.join(part_nums)
        # to include part relationships, add "&inc_part_details=1" to the url
        return F'https://rebrickable.com/api/v3/lego/parts/?part_nums={part_list_str}&key={api_key}&inc_part_details=1'

    def _load_scrape_data(self, json_file_path, part_csv_path):
        part_dic = {}
        part_nums = []

        # Read the scrape data from the existing json file
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as file_ptr:
                json_dic = json.load(file_ptr)

                part_nums = json_dic['unscraped_parts']
                part_dic = json_dic['parts']

                # Don't process a file if all parts are scraped
                if not part_nums:
                    raise CommandError(F'"{json_file_path}" has no unscraped parts. Select a different file')

        # Resume of previously scraped and not finished instead of starting new
        if part_csv_path:
            if not part_nums:
                part_nums = Command._get_part_nums_from_rebrickable_csv(part_csv_path)
            else:
                self.stdout.write(F'Parts CSV specified but need to complete unscraped parts first')

        # Backup, start scraping from the DB
        if not part_nums:
            part_nums = [x.part_num for x in Part.objects.all()]

        return (part_nums, part_dic)

    def _scrape(self, url):
        self.stdout.write(F'  Scraping Url: {url}')
        json_result = {}

        result = scraper.scrape_url(ScrapeConfig(url))
        if result.status == ScrapeStatus.SUCCESS:
            json_result = json.loads(result.first_page.html)
        else:
            self.stderr.write(F'Scraping Issue: {result.error_msg}')

        return json_result

    def _save_scrape(self, json_file_path, data_dic, unscraped_list):
        self.stdout.write(F'  Save Scrape State, Unscraped Items: {len(unscraped_list)}')
        json_dic = {}
        json_dic['unscraped_parts'] = unscraped_list
        json_dic['parts'] = data_dic

        with open(json_file_path, 'w', encoding='utf-8') as file_ptr:
            json.dump(json_dic, file_ptr)

    @staticmethod
    def _process_scrape_result(scrape_result, data_dic):
        for result in scrape_result['results']:
            result_dic = {}
            part_num = result['part_num']
            result_dic = result
            data_dic[part_num] = result_dic
        return data_dic
