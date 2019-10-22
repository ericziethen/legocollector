import json
import os
import time

from django.core.management.base import BaseCommand
from ezscrape.scraping import scraper
from ezscrape.scraping.core import ScrapeConfig
from ezscrape.scraping.core import ScrapeStatus

from inventory.models import Part


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('rebrickabe_api_key', type=str)
        parser.add_argument('json_file_path', type=str)

    def handle(self, *args, **options):
        self.parts_per_scrape = 100
        rebrickabe_api_key = options['rebrickabe_api_key']
        json_file_path = options['json_file_path']

        self.scrape_rebrickable_parts(rebrickabe_api_key, json_file_path)

    def scrape_rebrickable_parts(self, api_key, json_file_path):
        self.stdout.write(F'Scraping Rebrickable Parts')

        # Get the data to scrape
        part_nums, data_dic = self._load_scrape_data(json_file_path)

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
            time.sleep(1)

            # TODO - Remove
            import sys
            sys.exit(1)

        self.stdout.write(F'Scraping Complete')

    def scrape_rebrickable_parts_OLD(self, api_key, json_file_path):
        # Get the data to scrape

        ''' NEW PSEUDO code

            Get Scrape Data
                - full List of Part numbers to read (FUNCTION) -> Full Part Num List
                    - read from file, if no file or empty, get all from DB
                    - decide if want to return including previous issue list
                - current file data dic

            while split list in scrape_list and part_nums (FUNCTION, to handle less than full count left)
                -> Return 2 lists

                form url from scrape_list (FUNCTION)   -> Returns URL string

                scrape url (FUNCTION), return Raw Data Dic or None

                if scrape ok:
                    data_dic = process data received (MAYBE FUNCTION), combine existing with new data
                    sav current state (FUNCTION, data_dic, part_nums) in json, to continue with next

                else:
                    sav current state (FUNCTION, data_dic, part_nums+scrape_list) in json, to continue with next
                        - save 2 lists, outstanding + issue list

                wait 1 second

        '''


        self.stdout.write(F'Scraping Rebrickable Parts')
        json_dic = {}
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as fp:
                json_dic = json.load(fp)

        parts_on_url = 100
        parts = Part.objects.all()

        url_part_list = []
        for idx, part in enumerate(parts, 1):
            url_part_list.append(part.part_num)

            if len(url_part_list) % parts_on_url == 0:
                part_list_str = ','.join(url_part_list)
                # to include part relationships, add "&inc_part_details=1" to the url
                url = F'https://rebrickable.com/api/v3/lego/parts/?part_nums={part_list_str}&key={api_key}'

                # Scrape the URL:
                result = scraper.scrape_url(ScrapeConfig(url))

                '''
                !!! GOT: ERROR EXCEPTION: ReadTimeout - HTTPSConnectionPool(host='rebrickable.com', port=443): Read timed out. (read timeout=5.0)
                    -> Handle in EZSCRAPE or here???
                    -> Have a more logic way to resume later?
                    -> Maybe can store the list of items in the Dictionary first,
                    and work from there, removing some all the time
                '''

                if result.status == ScrapeStatus.SUCCESS:
                    json_result = json.loads(result.first_page.html)
                    #print(F'RESULT: {json_result}')
                else:
                    print('ERROR', result.error_msg)
                    import sys
                    sys.exit(1)


                # Disect the Data
                for result in json_result['results']:
                    data_dic = {}
                    part_num = result['part_num']
                    data_dic['external_ids'] = result['external_ids']
                    json_dic[part_num] = data_dic

                # Clear the list
                del url_part_list[:]

                with open(json_file_path, 'w', encoding='utf-8') as fp:
                    json.dump(json_dic, fp)

                self.stdout.write(F'  Processed Parts: {idx}')

                time.sleep(1)

    def _load_scrape_data(self, json_file_path):
        data_dic = {}
        part_nums = []

        if os.path.exists(json_file_path):
            # TODO - Load data from File
            pass

        ''' TODO
            if json file doesn't exist
                initialize empty base directory
            else
                read data dic from file
                read part_nums from file

            if part_nums empty
                fill part_num list with all part_nums in db
        '''

        # !!! TODO - Remove !!!
        part_nums = [str(x) for x in range(1020)]

        return (part_nums, data_dic)

    def _get_scrape_list(self, part_nums, count):
        scrape_list = []
        leftover_part_nums = []

        if len(part_nums) > count:
            scrape_list = part_nums[:count]
            leftover_part_nums = part_nums[count:]
        else:
            scrape_list = part_nums

        return (scrape_list, leftover_part_nums)

    def _form_scrape_url(self, part_nums, api_key):
        part_list_str = ','.join(part_nums)
        # to include part relationships, add "&inc_part_details=1" to the url
        return F'https://rebrickable.com/api/v3/lego/parts/?part_nums={part_list_str}&key={api_key}'

    def _scrape(self, url):
        self.stdout.write(F'  Scraping Url: {url}')
        json_result = {}

        ''' TODO - ENABLE FOR FULL TESTING
        result = scraper.scrape_url(ScrapeConfig(url))
        if result.status == ScrapeStatus.SUCCESS:
            json_result = json.loads(result.first_page.html)
        else:
            self.stderr.write(F'Scraping Issue: {result.error_msg}')
        '''

        # TODO - DISABLE WHEN DONE
        json_result = ERIC_JSON

        return json_result

    def _process_scrape_result(self, scrape_result, data_dic):
        for result in scrape_result['results']:
            result_dic = {}
            part_num = result['part_num']
            result_dic['external_ids'] = result['external_ids']
            data_dic[part_num] = result_dic

        return data_dic

    def _save_scrape(self, json_file_path, data_dic, unscraped_list):
        json_dic = {}
        json_dic['unscraped_parts'] = unscraped_list
        json_dic['parts'] = data_dic

        with open(json_file_path, 'w', encoding='utf-8') as fp:
            json.dump(json_dic, fp)


ERIC_JSON = {
    "count": 100,
    "next": 'null',
    "previous": 'null',
    "results": [
        {
            "part_num": "20953",
            "name": "Brick Round 2 x 2 Sphere with Stud [Plain]",
            "part_cat_id": 20,
            "part_url": "https://rebrickable.com/parts/20953/brick-round-2-x-2-sphere-with-stud-plain/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6221776.jpg",
            "external_ids": {},
            "print_of": 'null'
        },
        {
            "part_num": "20953pr0001",
            "name": "Brick Round 2 x 2 Sphere with Stud / Robot Body with BB-8 Droid Print",
            "part_cat_id": 20,
            "part_url": "https://rebrickable.com/parts/20953pr0001/brick-round-2-x-2-sphere-with-stud-robot-body-with-bb-8-droid-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6124643.jpg",
            "external_ids": {
                "BrickLink": [
                    "20953pb01"
                ],
                "BrickOwl": [
                    "378270"
                ],
                "LEGO": [
                    "23723"
                ]
            },
            "print_of": "20953"
        },
        {
            "part_num": "20953pr0002",
            "name": "Brick Round 2 x 2 Sphere with Stud / Robot Body with BB-9E Droid Print",
            "part_cat_id": 20,
            "part_url": "https://rebrickable.com/parts/20953pr0002/brick-round-2-x-2-sphere-with-stud-robot-body-with-bb-9e-droid-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6200061.jpg",
            "external_ids": {
                "BrickLink": [
                    "20953pb02"
                ],
                "BrickOwl": [
                    "994788"
                ],
                "LEGO": [
                    "35009"
                ]
            },
            "print_of": "20953"
        },
        {
            "part_num": "20953pr0003",
            "name": "Brick Round 2 x 2 Sphere with Stud with Chinese Lampoon print",
            "part_cat_id": 20,
            "part_url": "https://rebrickable.com/parts/20953pr0003/brick-round-2-x-2-sphere-with-stud-with-chinese-lampoon-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6258826.jpg",
            "external_ids": {
                "BrickLink": [
                    "20953pb03"
                ],
                "Brickset": [
                    "49994"
                ],
                "LEGO": [
                    "49994"
                ]
            },
            "print_of": "20953"
        },
        {
            "part_num": "20954",
            "name": "Minifig Cap, SW First Order Officer with Flap [Plain]",
            "part_cat_id": 24,
            "part_url": "https://rebrickable.com/parts/20954/minifig-cap-sw-first-order-officer-with-flap-plain/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/ldraw/-1/20954.png",
            "external_ids": {},
            "print_of": 'null'
        },
        {
            "part_num": "20954pr0001",
            "name": "Minifig Cap, SW First Order Officer with Black First Order Insignia and Black Flap Print",
            "part_cat_id": 65,
            "part_url": "https://rebrickable.com/parts/20954pr0001/minifig-cap-sw-first-order-officer-with-black-first-order-insignia-and-black-flap-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6124666.jpg",
            "external_ids": {
                "BrickLink": [
                    "20954pb02"
                ],
                "BrickOwl": [
                    "671690"
                ],
                "LEGO": [
                    "23732"
                ]
            },
            "print_of": "20954"
        },
        {
            "part_num": "20954pr0002",
            "name": "Minifig Cap, SW First Order Officer with Silver First Order Insignia Print (General Hux)",
            "part_cat_id": 65,
            "part_url": "https://rebrickable.com/parts/20954pr0002/minifig-cap-sw-first-order-officer-with-silver-first-order-insignia-print-general-hux/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6124667.jpg",
            "external_ids": {
                "BrickLink": [
                    "20954pb01"
                ],
                "BrickOwl": [
                    "46263"
                ],
                "LEGO": [
                    "23733"
                ]
            },
            "print_of": "20954"
        },
        {
            "part_num": "20954pr0003",
            "name": "Minifig Cap, SW First Order Officer with Black First Order Insignia and Black Flap Print",
            "part_cat_id": 65,
            "part_url": "https://rebrickable.com/parts/20954pr0003/minifig-cap-sw-first-order-officer-with-black-first-order-insignia-and-black-flap-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6188475.jpg",
            "external_ids": {
                "BrickLink": [
                    "20954pb02"
                ],
                "LEGO": [
                    "33578"
                ]
            },
            "print_of": "20954"
        },
        {
            "part_num": "20954pr0050",
            "name": "Minifig Cap, SW First Order Officer with Black/Red First Order Insignia Print",
            "part_cat_id": 65,
            "part_url": "https://rebrickable.com/parts/20954pr0050/minifig-cap-sw-first-order-officer-with-blackred-first-order-insignia-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6199916.jpg",
            "external_ids": {
                "BrickLink": [
                    "20954pb03"
                ],
                "BrickOwl": [
                    "961850"
                ],
                "LEGO": [
                    "34981"
                ]
            },
            "print_of": "20954"
        },
        {
            "part_num": "209656",
            "name": "Early Simple Machines III Teacher’s Guide",
            "part_cat_id": 17,
            "part_url": "https://rebrickable.com/parts/209656/early-simple-machines-iii-teachers-guide/",
            "part_img_url": 'null',
            "external_ids": {},
            "print_of": 'null'
        },
        {
            "part_num": "21",
            "name": "Windscreen 2 x 4 x 1 2/3",
            "part_cat_id": 47,
            "part_url": "https://rebrickable.com/parts/21/windscreen-2-x-4-x-1-23/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/ldraw/47/21.png",
            "external_ids": {
                "BrickOwl": [
                    "725421"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "210",
            "name": "Baseplate 16 x 22",
            "part_cat_id": 1,
            "part_url": "https://rebrickable.com/parts/210/baseplate-16-x-22/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/ldraw/2/210.png",
            "external_ids": {
                "BrickOwl": [
                    "770174"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21008pr0001",
            "name": "Cape with Iridescent Dots (Sequins) Pattern",
            "part_cat_id": 38,
            "part_url": "https://rebrickable.com/parts/21008pr0001/cape-with-iridescent-dots-sequins-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6112922.jpg",
            "external_ids": {
                "BrickLink": [
                    "21008pb01"
                ],
                "BrickOwl": [
                    "277165"
                ]
            },
            "print_of": "21008"
        },
        {
            "part_num": "21008pr0002",
            "name": "Cape with Gold Stars Pattern",
            "part_cat_id": 38,
            "part_url": "https://rebrickable.com/parts/21008pr0002/cape-with-gold-stars-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6164173.jpg",
            "external_ids": {
                "BrickLink": [
                    "21008pb02"
                ]
            },
            "print_of": "21008"
        },
        {
            "part_num": "21016",
            "name": "Sticker Sheet for Set 10248 - 21016/6112603",
            "part_cat_id": 58,
            "part_url": "https://rebrickable.com/parts/21016/sticker-sheet-for-set-10248-210166112603/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/photos/9999/10248stk01-9999-b2f7428d-7815-4be0-bc65-0e91cc4f57e5.jpg",
            "external_ids": {
                "BrickLink": [
                    "10248stk01"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21018pr0001",
            "name": "Minifig Poncho Cloth with Camouflage Print",
            "part_cat_id": 38,
            "part_url": "https://rebrickable.com/parts/21018pr0001/minifig-poncho-cloth-with-camouflage-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6112610.jpg",
            "external_ids": {
                "BrickLink": [
                    "21018pb01"
                ],
                "BrickOwl": [
                    "440838"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00",
            "name": "Legs and Hips [Multi-color Mold Injection]",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00/legs-and-hips-multi-color-mold-injection/",
            "part_img_url": 'null',
            "external_ids": {},
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat001",
            "name": "Legs and Hips with Bright Light Orange Boots [Donald]",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat001/legs-and-hips-with-bright-light-orange-boots-donald/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6143604.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0516"
                ],
                "BrickOwl": [
                    "573855"
                ],
                "LEGO": [
                    "21019"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat001pr1035",
            "name": "Legs and Hips with Bright Light Orange Boots Pattern with Bright Pink Shoes [Daisy]",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat001pr1035/legs-and-hips-with-bright-light-orange-boots-pattern-with-bright-pink-shoes-daisy/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6143662.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0515"
                ],
                "BrickOwl": [
                    "212334"
                ],
                "LEGO": [
                    "25884"
                ]
            },
            "print_of": "21019c00pat001"
        },
        {
            "part_num": "21019c00pat001pr1098",
            "name": "Legs and Hips with Bright Light Orange Boots Pattern with Medium Lavender Feet Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat001pr1098/legs-and-hips-with-bright-light-orange-boots-pattern-with-medium-lavender-feet-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6157751.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0559"
                ],
                "BrickOwl": [
                    "212778"
                ],
                "LEGO": [
                    "27221"
                ]
            },
            "print_of": "21019c00pat001"
        },
        {
            "part_num": "21019c00pat002",
            "name": "Legs and Hips with Red Boots Pattern",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat002/legs-and-hips-with-red-boots-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6120518.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0420"
                ],
                "LEGO": [
                    "21019"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat002pr1104",
            "name": "Legs and Hips with Red Boots Pattern with Black Lines on Knees",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat002pr1104/legs-and-hips-with-red-boots-pattern-with-black-lines-on-knees/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6158153.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0587"
                ],
                "BrickOwl": [
                    "484541"
                ],
                "LEGO": [
                    "27380"
                ]
            },
            "print_of": "21019c00pat002"
        },
        {
            "part_num": "21019c00pat002pr1197",
            "name": "Legs and Hips with Red Boots Pattern and Red Diamond Button, Pockets and Detailed Boots Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat002pr1197/legs-and-hips-with-red-boots-pattern-and-red-diamond-button-pockets-and-detailed-boots-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6176332.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0614"
                ],
                "BrickOwl": [
                    "29904",
                    "368770"
                ],
                "LEGO": [
                    "29904"
                ]
            },
            "print_of": "21019c00pat002"
        },
        {
            "part_num": "21019c00pat002pr1404",
            "name": "Legs and Hips with Red Boots Pattern with Yellow Laces, Yellow Belt (El Dorado)",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat002pr1404/legs-and-hips-with-red-boots-pattern-with-yellow-laces-yellow-belt-el-dorado/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6210439.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0776"
                ],
                "LEGO": [
                    "36204"
                ]
            },
            "print_of": "21019c00pat002"
        },
        {
            "part_num": "21019c00pat002pr1430",
            "name": "Legs and Hips with Red Boots Pattern with Yellow Stripes",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat002pr1430/legs-and-hips-with-red-boots-pattern-with-yellow-stripes/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6212873.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0766",
                    "970c00pb766"
                ],
                "LEGO": [
                    "36600"
                ]
            },
            "print_of": "21019c00pat002"
        },
        {
            "part_num": "21019c00pat002pr1523",
            "name": "Legs and Hips with Red Boots Pattern with Pockets and Laces, White Soles Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat002pr1523/legs-and-hips-with-red-boots-pattern-with-pockets-and-laces-white-soles-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6258694.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0833"
                ],
                "LEGO": [
                    "38772"
                ]
            },
            "print_of": "21019c00pat002"
        },
        {
            "part_num": "21019c00pat003",
            "name": "Legs and Hips with Dark Green Boots Pattern",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat003/legs-and-hips-with-dark-green-boots-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6207109.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0723"
                ],
                "BrickOwl": [
                    "578055"
                ],
                "LEGO": [
                    "21019"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat003pr1641",
            "name": "Legs and Hips with Dark Green Boots Pattern with Metal Plating, Knee Caps",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat003pr1641/legs-and-hips-with-dark-green-boots-pattern-with-metal-plating-knee-caps/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6254136.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0935"
                ],
                "LEGO": [
                    "48237"
                ]
            },
            "print_of": "21019c00pat003"
        },
        {
            "part_num": "21019c00pat003pr1667",
            "name": "Legs and Hips with Dark Green Boots and Black Belt, Gray Plaid, Black Toes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat003pr1667/legs-and-hips-with-dark-green-boots-and-black-belt-gray-plaid-black-toes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6257813.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0926"
                ],
                "LEGO": [
                    "50025"
                ]
            },
            "print_of": "21019c00pat003"
        },
        {
            "part_num": "21019c00pat004",
            "name": "Legs and Hips with Black Boots Pattern",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004/legs-and-hips-with-black-boots-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6120935.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0411"
                ],
                "BrickOwl": [
                    "996256"
                ],
                "LEGO": [
                    "21019"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat004pr0920",
            "name": "Legs and Hips with Black Boots Pattern with 3 Black and Gray Clasps and Black Boots Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr0920/legs-and-hips-with-black-boots-pattern-with-3-black-and-gray-clasps-and-black-boots-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6122705.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0444"
                ],
                "BrickOwl": [
                    "246692"
                ],
                "LEGO": [
                    "22830"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr0921",
            "name": "Legs and Hips with Black Boots Pattern with Black Stripes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr0921/legs-and-hips-with-black-boots-pattern-with-black-stripes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6122711.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0441"
                ],
                "BrickOwl": [
                    "193759"
                ],
                "LEGO": [
                    "22833"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr0982",
            "name": "Legs and Hips with Black Boots Pattern with Plaid Miniskirt, Dark Brown Tights print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr0982/legs-and-hips-with-black-boots-pattern-with-plaid-miniskirt-dark-brown-tights-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6132432.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0479"
                ],
                "LEGO": [
                    "24387"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1032",
            "name": "Legs and Hips with Black Boots Pattern and 2 White Buttons on Red Shorts and Yellow Shoes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1032/legs-and-hips-with-black-boots-pattern-and-2-white-buttons-on-red-shorts-and-yellow-shoes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6143246.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0518"
                ],
                "BrickOwl": [
                    "914415"
                ],
                "LEGO": [
                    "25840"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1033",
            "name": "Legs and Hips with Black Boots Pattern and White Ruffled Knickers and Dark Pink Shoes print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1033/legs-and-hips-with-black-boots-pattern-and-white-ruffled-knickers-and-dark-pink-shoes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6143273.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0520"
                ],
                "BrickOwl": [
                    "146399"
                ],
                "LEGO": [
                    "25843"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1097",
            "name": "Legs and Hips with Black Boots Pattern and Ruffles, Yellow Feet Print (Minnie)",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1097/legs-and-hips-with-black-boots-pattern-and-ruffles-yellow-feet-print-minnie/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6157648.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0558"
                ],
                "BrickOwl": [
                    "404821"
                ],
                "LEGO": [
                    "27218"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1106",
            "name": "Legs and Hips with Black Boots Pattern with 2 Pockets, Silver and Orange Stripes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1106/legs-and-hips-with-black-boots-pattern-with-2-pockets-silver-and-orange-stripes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6158209.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0557"
                ],
                "BrickOwl": [
                    "939545"
                ],
                "LEGO": [
                    "27387"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1108",
            "name": "Legs and Hips with Black Boots Pattern and Silver Belt and Chain, Knee Pads, Dark Bluish Gray Toes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1108/legs-and-hips-with-black-boots-pattern-and-silver-belt-and-chain-knee-pads-dark-bluish-gray-toes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6158458.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0535"
                ],
                "BrickOwl": [
                    "56388"
                ],
                "LEGO": [
                    "27425"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1120",
            "name": "Legs and Hips with Black Boots Pattern and 2 Cargo Pockets, Silver and Orange Stripes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1120/legs-and-hips-with-black-boots-pattern-and-2-cargo-pockets-silver-and-orange-stripes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6161518.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0556"
                ],
                "BrickOwl": [
                    "956157"
                ],
                "LEGO": [
                    "28224"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1214",
            "name": "Legs and Hips with Black Boots Pattern and Lab Coattails over Black Pants and ID Badge Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1214/legs-and-hips-with-black-boots-pattern-and-lab-coattails-over-black-pants-and-id-badge-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6176879.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0655"
                ],
                "LEGO": [
                    "30404"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1241",
            "name": "Legs and Hips with Black Boots Pattern with Long Coattail Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1241/legs-and-hips-with-black-boots-pattern-with-long-coattail-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6179960.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0745"
                ],
                "LEGO": [
                    "31881"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1403",
            "name": "Legs and Hips with Black Boots Pattern with White Boomerangs",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1403/legs-and-hips-with-black-boots-pattern-with-white-boomerangs/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6210429.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0795"
                ],
                "LEGO": [
                    "36192"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1439",
            "name": "Legs and Hips with Black Boots Print and Lab Coat Print (Hugo Strange)",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1439/legs-and-hips-with-black-boots-print-and-lab-coat-print-hugo-strange/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6214109.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0751"
                ],
                "BrickOwl": [
                    "579984"
                ],
                "LEGO": [
                    "36816"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1567",
            "name": "Legs and Hips with Black Boots Pattern, Dark Bluish Gray Center Panel Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1567/legs-and-hips-with-black-boots-pattern-dark-bluish-gray-center-panel-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6236415.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb853"
                ],
                "LEGO": [
                    "39559"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1582",
            "name": "Legs and Hips with Black Boots Pattern and Black belt, Reddish Brown Holster, Gray Belt Buckle",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1582/legs-and-hips-with-black-boots-pattern-and-black-belt-reddish-brown-holster-gray-belt-buckle/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6238640.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0893"
                ],
                "Brickset": [
                    "39896"
                ],
                "LEGO": [
                    "39896"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1589",
            "name": "Legs and Hips with Black Boots Pattern with White Toes",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1589/legs-and-hips-with-black-boots-pattern-with-white-toes/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6245436.jpg",
            "external_ids": {
                "Brickset": [
                    "42281"
                ],
                "LEGO": [
                    "42281"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1590",
            "name": "Legs and Hips with Black Boots Pattern and Skirt, White Shoes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1590/legs-and-hips-with-black-boots-pattern-and-skirt-white-shoes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6245509.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb962"
                ],
                "LEGO": [
                    "42439"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1605",
            "name": "Legs and Hips with Black Boots Pattern and Belt and Strap with Silver Buckles, Knee Pads, Pouch on Right Side Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1605/legs-and-hips-with-black-boots-pattern-and-belt-and-strap-with-silver-buckles-knee-pads-pouch-on-right-side-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6251155.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0898"
                ],
                "LEGO": [
                    "48116"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1732",
            "name": "Legs and Hips with Black Boots Pattern and Lab Coat Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1732/legs-and-hips-with-black-boots-pattern-and-lab-coat-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6267940.jpg",
            "external_ids": {
                "LEGO": [
                    "55654"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat004pr1755",
            "name": "Legs and Hips with Black Boots Pattern with Silver Toes",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1755/legs-and-hips-with-black-boots-pattern-with-silver-toes/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6274725.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c67pb01"
                ],
                "LEGO": [
                    "60409"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr1756",
            "name": "Legs and Hips with Black Boots Pattern and Dress/Ruffles, Silver Feet",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr1756/legs-and-hips-with-black-boots-pattern-and-dressruffles-silver-feet/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6274730.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0950"
                ],
                "Brickset": [
                    "60390"
                ],
                "LEGO": [
                    "60390"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr9923",
            "name": "Legs and Hips with Black Boots Pattern, Jacket/Coat, Pockets, Belt",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr9923/legs-and-hips-with-black-boots-pattern-jacketcoat-pockets-belt/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6120935.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb896"
                ]
            },
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr9930",
            "name": "Legs and Hips with Black Boots Pattern with Black and Dark Bluish Gray Print and Gun Print on Right Side (Winter Soldier)",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr9930/legs-and-hips-with-black-boots-pattern-with-black-and-dark-bluish-gray-print-and-gun-print-on-right-side-winter-soldier/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/photos/326/970c00pr9930-326-c00fcdc7-2a0a-4191-b044-df012739d22b.jpg",
            "external_ids": {},
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat004pr9931",
            "name": "Legs and Hips with Black Boots Pattern with Dark Brown Pockets, Blue Sash (Wong)",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat004pr9931/legs-and-hips-with-black-boots-pattern-with-dark-brown-pockets-blue-sash-wong/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/photos/320/970c00pr9931-320-d2a3f070-0f09-4b38-aa6b-0bfdb571367e.jpg",
            "external_ids": {},
            "print_of": "21019c00pat004"
        },
        {
            "part_num": "21019c00pat005",
            "name": "Legs and Hips with White Boots Pattern",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat005/legs-and-hips-with-white-boots-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6261460.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0965"
                ],
                "BrickOwl": [
                    "792429"
                ],
                "LEGO": [
                    "21019"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat005pr1039",
            "name": "Legs and Hips with White Boots Pattern and Gold Coat Trim and Legs with Gold Coat Trim, White Leggings and Black Boots print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat005pr1039/legs-and-hips-with-white-boots-pattern-and-gold-coat-trim-and-legs-with-gold-coat-trim-white-leggings-and-black-boots-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6145265.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0521"
                ],
                "BrickOwl": [
                    "543629"
                ],
                "LEGO": [
                    "26062"
                ]
            },
            "print_of": "21019c00pat005"
        },
        {
            "part_num": "21019c00pat005pr1041",
            "name": "Legs and Hips with White Boots Pattern and Black Bodysuit and Silver Toes print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat005pr1041/legs-and-hips-with-white-boots-pattern-and-black-bodysuit-and-silver-toes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6145169.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0514"
                ],
                "BrickOwl": [
                    "457884"
                ],
                "LEGO": [
                    "25907",
                    "26044"
                ]
            },
            "print_of": "21019c00pat005"
        },
        {
            "part_num": "21019c00pat005pr1123",
            "name": "Legs and Hips with White Boots Pattern and Red Shoes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat005pr1123/legs-and-hips-with-white-boots-pattern-and-red-shoes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6162678.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0591"
                ],
                "LEGO": [
                    "28315"
                ]
            },
            "print_of": "21019c00pat005"
        },
        {
            "part_num": "21019c00pat005pr1176",
            "name": "Legs and Hips with White Boots Pattern and 4 White Squares on Sides Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat005pr1176/legs-and-hips-with-white-boots-pattern-and-4-white-squares-on-sides-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6173692.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0615"
                ],
                "BrickOwl": [
                    "306284"
                ],
                "LEGO": [
                    "29308"
                ]
            },
            "print_of": "21019c00pat005"
        },
        {
            "part_num": "21019c00pat005pr1351",
            "name": "Legs and Hips with White Boots Pattern and Silver Belt, Pockets, Yellow Lightning Symbols, Knee Pads, Dark Bluish Gray Tips, Silver Chain",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat005pr1351/legs-and-hips-with-white-boots-pattern-and-silver-belt-pockets-yellow-lightning-symbols-knee-pads-dark-bluish-gray-tips-silver-chain/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6197117.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0705"
                ],
                "BrickOwl": [
                    "59880"
                ],
                "LEGO": [
                    "34674"
                ]
            },
            "print_of": "21019c00pat005"
        },
        {
            "part_num": "21019c00pat005pr1422",
            "name": "Legs and Hips with White Boots Pattern and Green Sandals",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat005pr1422/legs-and-hips-with-white-boots-pattern-and-green-sandals/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6211939.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0752"
                ],
                "BrickOwl": [
                    "223885"
                ],
                "LEGO": [
                    "36409"
                ]
            },
            "print_of": "21019c00pat005"
        },
        {
            "part_num": "21019c00pat005pr1494",
            "name": "Legs and Hips with White Boots Pattern and Cat Costume, White Fur Feet",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat005pr1494/legs-and-hips-with-white-boots-pattern-and-cat-costume-white-fur-feet/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6224525.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0809"
                ],
                "BrickOwl": [
                    "396630"
                ],
                "LEGO": [
                    "38404"
                ]
            },
            "print_of": "21019c00pat005"
        },
        {
            "part_num": "21019c00pat005pr1739",
            "name": "Legs and Hips with White Boots Pattern and White Decorative Legs",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat005pr1739/legs-and-hips-with-white-boots-pattern-and-white-decorative-legs/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6270425.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0975"
                ],
                "LEGO": [
                    "57690"
                ]
            },
            "print_of": "21019c00pat005"
        },
        {
            "part_num": "21019c00pat006",
            "name": "Legs and Hips with Dark Red Boots Pattern",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat006/legs-and-hips-with-dark-red-boots-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6129522.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0474"
                ],
                "BrickOwl": [
                    "996256"
                ],
                "LEGO": [
                    "21019"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat006pr1107",
            "name": "Legs and Hips with Dark Red Boots Pattern with Boxing Shorts with Red Trim and Laces",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat006pr1107/legs-and-hips-with-dark-red-boots-pattern-with-boxing-shorts-with-red-trim-and-laces/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6158397.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0538"
                ],
                "BrickOwl": [
                    "557327"
                ],
                "LEGO": [
                    "27417"
                ]
            },
            "print_of": "21019c00pat006"
        },
        {
            "part_num": "21019c00pat006pr9999",
            "name": "Legs and Hips with Dark Red Boots Pattern and Notch on Sides Print (Marceline)",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat006pr9999/legs-and-hips-with-dark-red-boots-pattern-and-notch-on-sides-print-marceline/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/photos/272/970c00pr9999-272-3cc9b73c-aa94-483f-982c-785d77c4df3f.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0645"
                ],
                "BrickOwl": [
                    "641679"
                ]
            },
            "print_of": "21019c00pat006"
        },
        {
            "part_num": "21019c00pat007pr1003",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Dark Orange dress Print (Possessed Dana)",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1003/legs-and-hips-with-light-flesh-boots-pattern-and-dark-orange-dress-print-possessed-dana/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6134925.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c90pb10"
                ],
                "LEGO": [
                    "24745"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1113",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Black Shoes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1113/legs-and-hips-with-light-flesh-boots-pattern-and-black-shoes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6159833.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0616"
                ],
                "LEGO": [
                    "27945"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1159",
            "name": "Legs and Hips with Light Flesh Boots and Dressing Gown Robe Tails with Black Brocade Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1159/legs-and-hips-with-light-flesh-boots-and-dressing-gown-robe-tails-with-black-brocade-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6170904.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0620"
                ],
                "BrickOwl": [
                    "571190"
                ],
                "LEGO": [
                    "29015"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1190",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Shorts with Yellow Bat Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1190/legs-and-hips-with-light-flesh-boots-pattern-and-shorts-with-yellow-bat-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6175373.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0617"
                ],
                "BrickOwl": [
                    "861865"
                ],
                "LEGO": [
                    "29751"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1400",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Green Swimming Trunks, 'R', Laces",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1400/legs-and-hips-with-light-flesh-boots-pattern-and-green-swimming-trunks-r-laces/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6210034.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0753"
                ],
                "LEGO": [
                    "36118"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1431",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Swimming Suit Black Stripes",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1431/legs-and-hips-with-light-flesh-boots-pattern-and-swimming-suit-black-stripes/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6212917.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0755"
                ],
                "LEGO": [
                    "36619"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1472",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Wavy Lines and Black Sandals with Silver Buckles Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1472/legs-and-hips-with-light-flesh-boots-pattern-and-wavy-lines-and-black-sandals-with-silver-buckles-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6218939.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c90pb13"
                ],
                "BrickOwl": [
                    "166346"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1550",
            "name": "Legs and Hips with Light Flesh Boots Pattern, Asymmetric Skirt, Black Shoes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1550/legs-and-hips-with-light-flesh-boots-pattern-asymmetric-skirt-black-shoes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6236113.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb854"
                ],
                "LEGO": [
                    "39505"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1711",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Wilma Flintstone Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1711/legs-and-hips-with-light-flesh-boots-pattern-and-wilma-flintstone-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6265475.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0940"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1712",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Fred Flintstone",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1712/legs-and-hips-with-light-flesh-boots-pattern-and-fred-flintstone/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6265476.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0939"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1713",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Barney Rubble Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1713/legs-and-hips-with-light-flesh-boots-pattern-and-barney-rubble-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6265480.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0941"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr1714",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Betty Rubble Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr1714/legs-and-hips-with-light-flesh-boots-pattern-and-betty-rubble-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6265483.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0942"
                ]
            },
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat007pr9934",
            "name": "Legs and Hips with Light Flesh Boots Pattern and Dark Pink Dress and Shoes Print (Dolores Umbridge)",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat007pr9934/legs-and-hips-with-light-flesh-boots-pattern-and-dark-pink-dress-and-shoes-print-dolores-umbridge/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/photos/5/970c00pr9934-5-4e2b0c4f-753c-48cb-87b7-8ba2a7197aa1.jpg",
            "external_ids": {},
            "print_of": "21019c00pat007"
        },
        {
            "part_num": "21019c00pat008",
            "name": "Legs and Hips with Dark Blue Boots Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat008/legs-and-hips-with-dark-blue-boots-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6160527.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0537"
                ],
                "BrickOwl": [
                    "132219"
                ],
                "LEGO": [
                    "21019"
                ]
            },
            "print_of": "21019c00"
        },
        {
            "part_num": "21019c00pat009",
            "name": "Legs and Hips with Blue Boots Pattern",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat009/legs-and-hips-with-blue-boots-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6152659.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0550"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat009pr1639",
            "name": "Legs and Hips with Blue Boots Pattern and Knee Pads, Olive Green Coat",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat009pr1639/legs-and-hips-with-blue-boots-pattern-and-knee-pads-olive-green-coat/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6254083.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0920",
                    "970c00pb920"
                ],
                "LEGO": [
                    "48159"
                ]
            },
            "print_of": "21019c00pat009"
        },
        {
            "part_num": "21019c00pat010",
            "name": "Legs and Hips with Yellow Boots Pattern",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat010/legs-and-hips-with-yellow-boots-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6192140.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0575"
                ],
                "BrickOwl": [
                    "273066",
                    "770879"
                ],
                "LEGO": [
                    "21019"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat010pr1116",
            "name": "Legs and Hips with Yellow Boots Pattern with Tattered Shorts with White Stripes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat010pr1116/legs-and-hips-with-yellow-boots-pattern-with-tattered-shorts-with-white-stripes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6160416.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0539"
                ],
                "BrickOwl": [
                    "474177"
                ],
                "LEGO": [
                    "28126"
                ]
            },
            "print_of": "21019c00pat010"
        },
        {
            "part_num": "21019c00pat010pr1187",
            "name": "Legs and Hips with Yellow Boots Pattern and Yellow Kneepads, Clasps on Side, Silver Belt Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat010pr1187/legs-and-hips-with-yellow-boots-pattern-and-yellow-kneepads-clasps-on-side-silver-belt-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6174459.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0641"
                ],
                "BrickOwl": [
                    "619013"
                ],
                "LEGO": [
                    "29491"
                ]
            },
            "print_of": "21019c00pat010"
        },
        {
            "part_num": "21019c00pat010pr1428",
            "name": "Legs and Hips with Yellow Boots Pattern and Red Paw Print Shorts and Yellow Feet Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat010pr1428/legs-and-hips-with-yellow-boots-pattern-and-red-paw-print-shorts-and-yellow-feet-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6212502.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0785"
                ],
                "LEGO": [
                    "36582"
                ]
            },
            "print_of": "21019c00pat010"
        },
        {
            "part_num": "21019c00pat010pr9959",
            "name": "Legs and Hips with Yellow Boots Pattern and Swimming Trunks, Laces, Sandals",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat010pr9959/legs-and-hips-with-yellow-boots-pattern-and-swimming-trunks-laces-sandals/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/photos/14/970c00pr9959-14-5e78baca-f47f-4807-b970-ed0b1680fb6f.jpg",
            "external_ids": {},
            "print_of": "21019c00pat010"
        },
        {
            "part_num": "21019c00pat011pr1109",
            "name": "Legs and Hips with Reddish Brown Boots Pattern and Dark Green Belt Tie, Dark Orange Toes Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat011pr1109/legs-and-hips-with-reddish-brown-boots-pattern-and-dark-green-belt-tie-dark-orange-toes-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6159525.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0534"
                ],
                "BrickOwl": [
                    "745012"
                ],
                "LEGO": [
                    "27464"
                ]
            },
            "print_of": "21019c00pat011"
        },
        {
            "part_num": "21019c00pat011pr1111",
            "name": "Legs and Hips with Reddish Brown Boots Pattern and Belt Loops, 2 Pockets with 2 Buttons Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat011pr1111/legs-and-hips-with-reddish-brown-boots-pattern-and-belt-loops-2-pockets-with-2-buttons-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6159667.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0536"
                ],
                "BrickOwl": [
                    "322255"
                ],
                "LEGO": [
                    "27484"
                ]
            },
            "print_of": "21019c00pat011"
        },
        {
            "part_num": "21019c00pat011pr1114",
            "name": "Legs and Hips with Reddish Brown Boots Pattern and Reddish Brown Belt, Pouch Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat011pr1114/legs-and-hips-with-reddish-brown-boots-pattern-and-reddish-brown-belt-pouch-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6159898.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0540"
                ],
                "BrickOwl": [
                    "373347"
                ],
                "LEGO": [
                    "27952"
                ]
            },
            "print_of": "21019c00pat011"
        },
        {
            "part_num": "21019c00pat011pr1170",
            "name": "Legs and Hips with Reddish Brown Boots Pattern and Caveman Belt and Skirt, Light Flesh Knees Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat011pr1170/legs-and-hips-with-reddish-brown-boots-pattern-and-caveman-belt-and-skirt-light-flesh-knees-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6173316.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0613"
                ],
                "BrickOwl": [
                    "290665"
                ],
                "LEGO": [
                    "29265"
                ]
            },
            "print_of": "21019c00pat011"
        },
        {
            "part_num": "21019c00pat011pr1267",
            "name": "Legs and Dark Tan Hips with Reddish Brown Boots Pattern and Belt and Dark Tan Loincloth Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat011pr1267/legs-and-dark-tan-hips-with-reddish-brown-boots-pattern-and-belt-and-dark-tan-loincloth-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6185527.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c03pb31"
                ],
                "BrickOwl": [
                    "873773"
                ],
                "LEGO": [
                    "32919"
                ]
            },
            "print_of": "21019c00pat011"
        },
        {
            "part_num": "21019c00pat011pr1522",
            "name": "Legs and Hips with Reddish Brown Boots Pattern and Brown Belt, White Socks",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat011pr1522/legs-and-hips-with-reddish-brown-boots-pattern-and-brown-belt-white-socks/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6227252.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0818"
                ],
                "BrickOwl": [
                    "837731"
                ],
                "LEGO": [
                    "38769"
                ]
            },
            "print_of": "21019c00pat011"
        },
        {
            "part_num": "21019c00pat011pr1635",
            "name": "Legs and Hips with Reddish Brown Boots Pattern and Metal Plating, Steel toes, Knee Caps",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat011pr1635/legs-and-hips-with-reddish-brown-boots-pattern-and-metal-plating-steel-toes-knee-caps/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6253993.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0936"
                ],
                "LEGO": [
                    "48207"
                ]
            },
            "print_of": "21019c00pat011"
        },
        {
            "part_num": "21019c00pat011pr1665",
            "name": "Legs and Hips with Reddish Brown Boots, Orange Giraffe Spots Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat011pr1665/legs-and-hips-with-reddish-brown-boots-orange-giraffe-spots-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6256555.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0921"
                ],
                "LEGO": [
                    "49988"
                ]
            },
            "print_of": "21019c00pat011"
        },
        {
            "part_num": "21019c00pat012",
            "name": "Legs and Hips with Dark Brown Boots Pattern",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat012/legs-and-hips-with-dark-brown-boots-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6139200.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0495"
                ]
            },
            "print_of": 'null'
        },
        {
            "part_num": "21019c00pat012pr1219",
            "name": "Legs and Hips with Dark Brown Boots Pattern and Tartan Kilt, Dark Brown Belt Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat012pr1219/legs-and-hips-with-dark-brown-boots-pattern-and-tartan-kilt-dark-brown-belt-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/photos/118/970c00pr1219-118-8acfddaf-e4a7-4cf9-9a72-6cc07531b5ff.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb629"
                ]
            },
            "print_of": "21019c00pat012"
        },
        {
            "part_num": "21019c00pat012pr1265",
            "name": "Legs and Hips with Dark Brown Boots Pattern and Light Bluish Gray Long Coattail Outlines Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat012pr1265/legs-and-hips-with-dark-brown-boots-pattern-and-light-bluish-gray-long-coattail-outlines-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6186022.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0671"
                ],
                "BrickOwl": [
                    "92133"
                ],
                "LEGO": [
                    "32950"
                ]
            },
            "print_of": "21019c00pat012"
        },
        {
            "part_num": "21019c00pat012pr1566",
            "name": "Legs and Hips with Dark Brown Boots, Dark Brown Pants, and Coattails Print",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat012pr1566/legs-and-hips-with-dark-brown-boots-dark-brown-pants-and-coattails-print/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6236416.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb852"
                ],
                "LEGO": [
                    "39560"
                ]
            },
            "print_of": "21019c00pat012"
        },
        {
            "part_num": "21019c00pat013",
            "name": "Legs and Hips with Dark Purple Boots Pattern",
            "part_cat_id": 61,
            "part_url": "https://rebrickable.com/parts/21019c00pat013/legs-and-hips-with-dark-purple-boots-pattern/",
            "part_img_url": "https://cdn.rebrickable.com/media/parts/elements/6256681.jpg",
            "external_ids": {
                "BrickLink": [
                    "970c00pb0922"
                ]
            },
            "print_of": 'null'
        }
    ]
}
