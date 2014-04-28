#!/usr/bin/env python3

import bs4
import os
import pickle
import re
import sys
import time
import urllib.request

reviews_per_member = 300
max_member_cnt = 300
city_id = 1     # For Shanghai
shop_type = 10  # For only food


def get_html(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"}
    #headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0"}
    req = urllib.request.Request(url=url, headers=headers)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError:
        print("Cannot open \'%(url)s\'" % {"url": url})
        exit(-1)
    html_page = response.read().decode("utf-8")
    response.close()
    return html_page


def get_memberlist_url(page: int):
    return """http://www.dianping.com/memberlist/%(city_id)d?pg=%(page)d""" % {
        "city_id": city_id,
        "page": page
    }


def get_homepage_url(member_id: str):
    return """http://www.dianping.com/member/%(member_id)s""" % {
        "member_id": member_id
    }


def get_review_url(member_url: str, page: int):
    return """%(member_url)s/reviews?pg=%(page)d&reviewCityId=%(city_id)d&reviewShopType=%(shop_type)d&c=1&shopTypeIndex=1""" % {
        "city_id": city_id,
        "member_url": member_url,
        "page": page,
        "shop_type": shop_type,
    }


def get_member_list_page_num(member_list_page_url: str):
    member_list_page = get_html(member_list_page_url)
    member_list_page_soup = bs4.BeautifulSoup(member_list_page)
    html_body = member_list_page_soup.body
    main_w = html_body.find("div", attrs={"class": "main_w"})
    content_a = main_w.find("div", attrs={"class": "content_a"})
    member_rank = content_a.find("div", attrs={"class": "box memberRank"})
    pages = member_rank.find("div", attrs={"class": "Pages"})
    page_nums = pages.find_all("a", attrs={"class": "PageLink", "title": True, "data-pg": True, "href": True})
    max_page_num = max(map(lambda a: int(a["title"]), page_nums))
    return max_page_num


def parser_member_url(member_list_url: str):
    member_page = get_html(member_list_url)
    member_soup = bs4.BeautifulSoup(member_page)
    html_body = member_soup.body
    main_w = html_body.find("div", attrs={"class": "main_w"})
    content_a = main_w.find("div", attrs={"class": "content_a"})
    member_rank = content_a.find("div", attrs={"class": "box memberRank"})
    member_table = member_rank.find("table", attrs={"class": "rankTable"})
    member_table_body = member_table.tbody
    member_list = member_table_body.find_all("tr")[1:]
    member_id = list(map(lambda m: m.find_all("td")[-1].a["data-userid"],
                         member_list))
    member_homepage_url = list(map(get_homepage_url, member_id))
    return member_homepage_url


def parser_review(member_url: str):
    member_id = int(os.path.split(member_url)[1])
    review_url = get_review_url(member_url, 1)
    review_page = get_html(review_url)
    review_soup = bs4.BeautifulSoup(review_page)
    review_body = review_soup.body
    review_wrapper = review_body.find("div", attrs={"class": "wrapper"})
    review_container_box = review_wrapper.find("div", attrs={"class": "container-box pages p-reviews"})
    review_container = review_container_box.find("div", attrs={"class": "container"})
    review_main = review_container.find("div", attrs={"class": "main"})
    review_modebox = review_main.find("div", attrs={"class": "modebox comm-list", "id": "J_review"})
    review_pages_num = review_modebox.find("div", attrs={"class": "pages-num"})
    review_total_page = max(map(lambda a: int(a["data-pg"]),
                                review_pages_num.find_all("a", attrs={"data-pg": True})))
    reviews = []
    for page_num in range(1, review_total_page + 1):
        print("page_num = %d" % page_num)
        review_url = get_review_url(member_url, page_num)
        review_page = get_html(review_url)
        review_soup = bs4.BeautifulSoup(review_page)
        review_body = review_soup.body
        review_wrapper = review_body.find("div", attrs={"class": "wrapper"})
        review_container_box = review_wrapper.find("div", attrs={"class": "container-box pages p-reviews"})
        review_container = review_container_box.find("div", attrs={"class": "container"})
        review_main = review_container.find("div", attrs={"class": "main"})
        review_modebox = review_main.find("div", attrs={"class": "modebox comm-list", "id": "J_review"})
        review_pic_txt = review_modebox.find("div", attrs={"class": "pic-txt"})
        review_ul = review_pic_txt.ul
        review_comment = review_ul.find_all("li")
        for comment in review_comment:
            try:
                comment_info = comment.find("div", attrs={"class": "txt J_rptlist"})
                shop_id_str = comment_info.find("div", attrs={"class": "tit"}).h6.a["href"]
                shop_id = int(os.path.split(shop_id_str)[1])
                comment_txt_c = comment_info.find("div", attrs={"class": "txt-c"})
                comment_mode_tc = comment_txt_c.find("div", attrs={"class": "mode-tc comm-rst"})
                spans = comment_mode_tc.find_all("span")
                rank = 0
                taste = 0
                environment = 0
                service = 0
                idx = 1
                try:
                    rank = int(spans[0]["class"][1][-2:])
                except KeyError:
                    idx = 0
                try:
                    taste = int(spans[idx + 0].getText()[3])
                except ValueError:
                    pass
                try:
                    environment = int(spans[idx + 1].getText()[3])
                except ValueError:
                    pass
                try:
                    service = int(spans[idx + 2].getText()[3])
                except ValueError:
                    pass
                reviews.append([shop_id, member_id, rank, taste, environment, service])
                if len(reviews) == reviews_per_member:
                    break
            except AttributeError:
                pass
        if len(reviews) == reviews_per_member:
            break
    return reviews


if __name__ == "__main__":
    member_cnt = 0
    if not os.path.exists("data"):
        os.mkdir("data")
    elif not os.path.isdir("data"):
        print("Error: Cannot create directory \'data/\'.", file=sys.stderr)
        exit(-1)
    member_list_page_num = get_member_list_page_num(get_memberlist_url(1))
    print(member_list_page_num)
    for i in range(1, member_list_page_num + 1):
        member_list_url = get_memberlist_url(i)
        member_list = parser_member_url(member_list_url)
        for member in member_list:
            member_cnt += 1
            print("member_cnt = %d" % member_cnt)
            if os.path.exists("data/%d.txt" % member_cnt):
                continue
            member_review = parser_review(member)
            dump_file = open("data/%d.txt" % member_cnt, "wb")
            pickle.dump(member_review, dump_file)
            dump_file.close()
            time.sleep(5)
            if member_cnt == max_member_cnt:
                break
        if member_cnt == max_member_cnt:
            break
