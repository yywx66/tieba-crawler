#coding=utf-8
from scrapy import Request
from cookieSpider import CookieSpider as Spider
from scrapy.selector import Selector
from dirbot.settings import TIEBA_NAMES_LIST
from dirbot.items import Post
import logging

class PostSpider(Spider):

    """Docstring for PostSpider. """

    name = 'post'
    allowed_domains = ["baidu.com"]

    def _extract_post_id(self, href):# href = /p/123456789
        try:
            return href.split('/')[-1]
        except Exception, e:
            return -1#没有ID的帖子就是广告，在pipeline里要过滤掉

    def start_requests(self):
        """TODO: Docstring for start_requests.
        :returns: TODO

        """
        url_list = map(
            lambda name: ("http://tieba.baidu.com/f?ie=utf-8&kw=" + name),
            TIEBA_NAMES_LIST
        )

        for url in url_list:
            yield Request(url, callback=self.parse)

    def _parse_posts(self, response):
        """TODO: Docstring for _parse_posts.

        :response: TODO
        :returns: TODO

        """
        logging.debug('parsing a post..')
        tieba_name = Selector(response).css('.card_title_fname::text').extract_first().strip()[:-1]# XX吧 -> XX
        post_item_sels = Selector(response).css('#thread_list>li')
        logging.debug('posts total num: %s', len(post_item_sels))

        for sel in post_item_sels:
            item = Post()
            item['tieba_name'] = tieba_name
            logging.debug('post id: %s' % (sel.css('.j_th_tit a::attr(href)').extract_first()))
            item['id'] = self._extract_post_id(sel.css('.j_th_tit a::attr(href)').extract_first())
            item['title'] = sel.css('.j_th_tit a::text').extract_first()# 有时标题过长会被截断，在帖子回复爬虫里再爬一遍完整的标题
            item['reply_num'] = sel.css('.threadlist_rep_num::text').extract_first()# 这里有可能是‘推广’,而非数字，在pipeline里过滤一遍
            item['author_name'] = sel.css('.tb_icon_author a::text').extract_first()
            item['body'] = sel.css('.threadlist_detail .threadlist_abs_onlyline::text').extract_first().strip()
        #item['post_time'] = sel.css('') #这里拿不到发贴时间，只有最后回复时间
            logging.debug('帖子：%r' % (item))

            yield item



    def parse(self, response):
        """TODO: Docstring for pass.

        :response: TODO
        :returns: TODO

        """
        logging.debug('begin parsing..')
        for item in self._parse_posts(response):
            yield item

        if len(Selector(response).css('.next.pagination-item')):
            pass
            #yield Request(Selector(response).css('.next.pagination-item::attr(href)').extract_first(), callback=self.parse)

