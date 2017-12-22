# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html


import scrapy

class Topic(scrapy.Item):
    topic_id = scrapy.Field()

    topic_title = scrapy.Field()
    topic_tags = scrapy.Field()
    topic_body = scrapy.Field()
    topic_user_mid = scrapy.Field()
    topic_user_name = scrapy.Field()
    topic_created_time = scrapy.Field()

    # tags

class Comment(scrapy.Item):
    topic_id = scrapy.Field()
    comment_id = scrapy.Field()
    comment_message = scrapy.Field()
    comment_user_mid = scrapy.Field()
    comment_user_name = scrapy.Field()
    comment_created_time = scrapy.Field()