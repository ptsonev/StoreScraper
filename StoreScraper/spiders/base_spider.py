import logging
import math
import re
from abc import ABC
from urllib.parse import quote

import haversine
import scrapy.core.scraper
import scrapy.utils
import scrapy.utils.misc
from scrapy import Request
from scrapy.http import Response
from scrapy.utils.project import get_project_settings


def warn_on_generator_with_return_value_stub(spider, callable):
    pass


scrapy.utils.misc.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub
scrapy.core.scraper.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub


class BaseSpider(scrapy.Spider, ABC):
    name = 'base_spider'
    country = 'DE'

    DEFAULT_AJAX_REQUEST_HEADER = {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    }

    def __init__(self, *args, **kwargs):
        super(BaseSpider).__init__(*args, **kwargs)
        self.configure_logging_extended()
        self.mapbox_api_key = get_project_settings().get('MAPBOX_API_KEY')

    @staticmethod
    def configure_logging_extended(logging_format: str = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'):
        modules = [
            # 'scrapy.statscollectors',
            'scrapy.crawler',
            'scrapy.utils.log',
            'scrapy.middleware',
            'scrapy.core.engine',
            'scrapy.core.scraper',
            'scrapy.addons',
            __name__
        ]
        for module in modules:
            logger = logging.getLogger(module)
            logger.setLevel(logging.WARNING)

        for handler in logging.root.handlers:
            handler.formatter = NoTracebackFormatter(logging_format)
            handler.addFilter(ContentFilter())

    @staticmethod
    def calculate_coordinates(radius: int = 100, unit: haversine.Unit = haversine.Unit.KILOMETERS, ne_coordinates=(55.1, 15.5), sw_coordinates=(47.2, 5.5)):
        nw_coordinates = (ne_coordinates[0], sw_coordinates[1])

        NW_NE_DISTANCE = math.ceil(haversine.haversine(nw_coordinates, ne_coordinates, unit=unit))
        NW_SW_DISTANCE = math.ceil(haversine.haversine(nw_coordinates, sw_coordinates, unit=unit))
        result_coordinates = []
        for h_distance in range(0, NW_SW_DISTANCE, radius):
            start_coordinates = haversine.inverse_haversine(nw_coordinates, h_distance, haversine.Direction.SOUTH)
            for w_distance in range(0, NW_NE_DISTANCE, radius):
                new_coordinates = haversine.inverse_haversine(start_coordinates, w_distance, haversine.Direction.EAST)
                result_coordinates.append(new_coordinates)
                # print(f'{new_coordinates[0]},{new_coordinates[1]},')

        return result_coordinates

    def parse_address(self, input_string: str) -> tuple[str, str, str]:
        try:
            address_parts = input_string.split(',')
            street = address_parts[0:-1][0]
            postal_code_match = re.search('\\d+', address_parts[-1])
            if postal_code_match is None:
                pass
            postal_code = postal_code_match.group(0) if postal_code_match else ''
            city = address_parts[-1].replace(postal_code, '')
            return street.strip(), postal_code.strip(), city.strip()

        except Exception as ex:
            self.logger.error('Error parsing address: %s', input_string)
            return '', '', ''

    def add_unique_address_id(self, item):
        """
        Probably should have done it with a middleware, but this is fine as well.
        :param item:
        :return:
        """
        if not self.mapbox_api_key:
            return item

        country = 'Germany' if self.country == 'DE' else 'Denmark'

        if item.get('Address'):
            address_parts = [
                item.get('Address'),
                item.get('City'),
                item.get('Zip'),
                country
            ]
        elif item.get('Latitude') and item.get('Longitude'):
            address_parts = [
                item.get('Longitude'),
                item.get('Latitude'),
            ]

        else:
            return item

        query = quote(','.join([a for a in address_parts if a]))

        url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={self.mapbox_api_key}'
        return Request(url=url, callback=self.parse_mapbox_api, cb_kwargs={'item': item})

    @staticmethod
    def parse_mapbox_api(response: Response, **kwargs):
        item = kwargs.get('item')

        feature = response.jmespath('features[*]').getall()[0]
        item['Longitude'] = item.get('Longitude') or feature['center'][0]
        item['Latitude'] = item.get('Latitude') or feature['center'][1]

        item['MapboxId'] = feature['id']
        item['MapboxAddress'] = feature['place_name']

        yield item


class ContentFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'spider'):
            record.name = record.spider.name
        elif hasattr(record, 'crawler'):
            record.name = record.crawler.spidercls.name
        else:
            pass
        return True


class NoTracebackFormatter(logging.Formatter):
    def formatException(self, ei):
        # return ''
        pass

    def formatStack(self, stack_info):
        # return ''
        pass
