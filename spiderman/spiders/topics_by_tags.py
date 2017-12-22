import dateutil.parser
import time
import json
import scrapy

# from termcolor import cprint
from scrapy import Selector
from scrapy.spiders import Spider
from spiderman.items import Topic, Comment
from spiderman.instruction import instruction


class PantipTopicsByTags(Spider):
    description = 'Pantip topics and comments by tags'
    download_delay = 1

    default_config = {}

    instruction = instruction

    instruction_schema = {
        'tags': {
            'description': 'List of tag',
            'type': 'array of string'
        }
    }

    name = 'pantip'
    allowed_domains = ["pantip.com"]

    def __init__(self):
        self.counter = 0

    def start_requests(self):
        tags = self.instruction.get('tags')

        for tag in tags:
            url = 'https://pantip.com/tag/{}'.format(tag)

            yield scrapy.Request(
                url=url,
                callback=self.parse_topic_list,
                meta={'tag': tag}
            )

    def parse_topic_list(self, response):
        self.counter += 1
        selector = Selector(response)
        topic_list = selector.xpath(
            '//div[contains(@class, "post-list-wrapper")]')
        topic_items = topic_list.css('div.post-item')

        for each_topic in topic_items:
            topic_link = each_topic.css(
                'div.post-item-title a::attr(href)').extract_first()
            topic_id = topic_link.rpartition('/')[2]

            comment_link = 'https://pantip.com/forum/topic/render_comments?tid={}'.format(topic_id)

            if len(topic_id) == 8:
                yield scrapy.Request(
                    url=response.urljoin(topic_link),
                    callback=self.parse_topic_content,
                    meta={'topic_id': topic_id})

                yield scrapy.Request(
                    url=response.urljoin(comment_link),
                    callback=self.parse_topic_comments,
                    headers={'X-Requested-With': 'XMLHttpRequest'},
                    meta={'topic_id': topic_id})

        yield self.paginate(response)

    def parse_topic_content(self, response):
        selector = Selector(response)
        topicSelector = selector.xpath('//div[contains(@class, "display-post-wrapper")]')

        main_post_inner = topicSelector[0].css('.main-post')
        post_tags = main_post_inner[0].css('.display-post-tag-wrapper')

        topic_title = main_post_inner.css('.display-post-title::text').extract_first()
        topic_body = main_post_inner.css('.display-post-story::text').extract_first()
        topic_user_name = main_post_inner.css('.display-post-name::text').extract_first()
        topic_user_mid = main_post_inner.css('.display-post-name::attr(id)').extract_first()
        topic_created_time_text = main_post_inner.css('.display-post-timestamp').css(
            '.timeago::attr(data-utime)').extract_first()

        tags_list = post_tags.css('.tag-item::text').extract()
        topic_tags = ','.join(tags_list)

        topic_body_1 = topic_body.replace('\r\n', '')
        topic_body_2 = topic_body_1.replace('\t', '')

        topic_created_time = str(int(time.mktime(dateutil.parser.parse(topic_created_time_text).timetuple())))

        topic_item = Topic()
        topic_item['topic_id'] = response.meta['topic_id']
        topic_item['topic_title'] = topic_title
        topic_item['topic_body'] = topic_body_2
        topic_item['topic_user_mid'] = topic_user_mid
        topic_item['topic_user_name'] = topic_user_name
        topic_item['topic_tags'] = topic_tags
        topic_item['topic_created_time'] = topic_created_time

        yield topic_item

    def parse_topic_comments(self, response):
        response_json = json.loads(response.body.decode("utf-8"))
        topic_id = response_json['paging']['topic_id']

        for comment in response_json['comments']:
            comment_id = comment['_id']
            comment_message = comment['message']
            comment_user_mid = comment['user']['mid']
            comment_user_name = comment['user']['name']
            comment_created_time = comment['created_time']

            comment_message_1 = comment_message.replace('\n', ' ')
            comment_message_2 = comment_message_1.replace('<br />', '')
            
            comment_item = Comment()
            comment_item['topic_id'] = topic_id
            comment_item['comment_id'] = comment_id
            comment_item['comment_message'] = comment_message_2
            comment_item['comment_user_mid'] = comment_user_mid
            comment_item['comment_user_name'] = comment_user_name
            comment_item['comment_created_time'] = comment_created_time

            yield comment_item

    def paginate(self, response):
        selector = Selector(response)
        load_more_link = selector.css('.loadmore-bar a::attr(href)').extract_first()

        if load_more_link is not None and self.counter < 1:
            return scrapy.Request(
                url=response.urljoin(load_more_link), 
                callback=self.parse_topic_list)
