import logging
import os
from os.path import exists

from colorama import Fore, Style, init
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from StoreScraper.spiders import PanasonicSpider, DaikinSpider, WeishauptSpider, BuderusSpider, WolfSpider, NibeSpider, BoschSpider, ViessmannSpider, VaillantSpider, AlphaInnotecSpider, WaermepumpeSpider, \
    VdiSpider, PanasonicDkSpider, DaikinDkSpider, VeinstallatoerDkSpider, ViessmannDkSpider, VaillantDkSpider, BoschDkSpider, DvienergiDkSpider, KinnanDkSpider, SparenergiDkSpider
from excel_exporter import excel_exporter, group_by_mapbox_id

logger = logging.getLogger(__name__)


def main():
    init()

    # os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'settings')

    settings = get_project_settings()

    data_file = settings.get('DATA_FILE')
    excel_file = settings.get('EXCEL_FILE')
    grouped_file = settings.get('GROUPED_FILE')

    if exists(data_file):
        os.remove(data_file)

    os.environ.setdefault('HTTP_PROXY', settings.get('HTTP_PROXY'))
    os.environ.setdefault('HTTPS_PROXY', settings.get('HTTP_PROXY'))

    process = CrawlerProcess(settings, install_root_handler=False)
    # logging
    configure_logging()

    ## GERMAN STORES
    # process.crawl(DaikinSpider)
    # process.crawl(WeishauptSpider)
    # process.crawl(BuderusSpider)
    # process.crawl(WolfSpider)
    # process.crawl(NibeSpider)
    # process.crawl(PanasonicSpider)
    # process.crawl(BoschSpider)
    # process.crawl(ViessmannSpider)
    # process.crawl(VaillantSpider)
    # process.crawl(AlphaInnotecSpider)
    # process.crawl(WaermepumpeSpider)
    # process.crawl(VdiSpider)

    ## DENMARK STORES
    ## Veinstallatoer has no address

    process.crawl(VeinstallatoerDkSpider)
    process.crawl(PanasonicDkSpider)
    process.crawl(DaikinDkSpider)
    process.crawl(ViessmannDkSpider)
    process.crawl(VaillantDkSpider)
    process.crawl(BoschDkSpider)
    process.crawl(DvienergiDkSpider)
    process.crawl(KinnanDkSpider)
    process.crawl(SparenergiDkSpider)

    process.start(install_signal_handlers=True)

    logger.info('SCRAPING COMPLETED.')
    try:
        logger.info('EXPORTING THE DATA TO EXCEL...')
        excel_exporter(data_file, excel_file)
        logger.info(f'{Fore.GREEN}{excel_file} was successfully saved.{Style.RESET_ALL}')

        logger.info('GROUPING THE DATA...')
        group_by_mapbox_id(excel_file, output_excel_file=grouped_file)
        logger.info(f'{Fore.GREEN}{grouped_file} was successfully saved.{Style.RESET_ALL}')

    except Exception as ex:
        logger.error(f'{Fore.RED}{ex}{Style.RESET_ALL}', exc_info=False, stack_info=False)

    finally:
        input('Press Enter to exit the program...')


if __name__ == '__main__':
    main()
