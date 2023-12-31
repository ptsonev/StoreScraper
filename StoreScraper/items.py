# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re

import scrapy
from email_validator import validate_email, EmailNotValidError
from itemloaders.processors import MapCompose, TakeFirst
from scrapy import Field
from url_normalize import url_normalize


def format_whitespaces(input_string: str) -> str:
    if not input_string:
        return ''
    return re.sub('\s+', ' ', input_string).strip()


def format_email(input_string: str) -> str:
    if input_string:
        try:
            formatted_string = input_string.replace(' ', '').replace('mailto:', '')
            email_info = validate_email(formatted_string, check_deliverability=False)
            return email_info.normalized.lower()
        except EmailNotValidError:
            pass
    return ''


def format_website(input_string: str) -> str:
    try:
        return url_normalize(input_string)
    except:
        return ''


class StoreItem(scrapy.Item):
    Source = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    Name1 = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    Name2 = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    Address = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    City = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    Zip = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    Email = Field(input_processor=MapCompose(format_whitespaces, format_email), output_processor=TakeFirst())
    Phone = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    Website = Field(input_processor=MapCompose(format_whitespaces, format_website), output_processor=TakeFirst())
    Latitude = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    Longitude = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())

    MapboxId = Field(output_processor=TakeFirst())
    MapboxAddress = Field(output_processor=TakeFirst())
    EmailDomain = Field(output_processor=TakeFirst())
    Gmbh = Field(output_processor=TakeFirst())
