import os
import re
import yaml
import math
import shutil
import json
import datetime

RE_RULER = r'^-{3}[\s\S]*-{3}\n'
BASE_PATH = os.getcwd()


def init():
    """
    删除原来的dist文件夹，创建一个新的
    """
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    os.mkdir('dist')


def get_all_md():
    """
    get all markdown posts and return a list which include absolute path for posts

    Returns:
        post: List[path]
    """
    os.chdir('normal')

    posts = os.listdir()
    for index, name in enumerate(posts):
        posts[index] = os.path.abspath(name)

    os.chdir(BASE_PATH)
    return posts


def get_all_friend_links():
    os.chdir('links')

    files = os.listdir()
    links = []
    for name in files:
        if name.split('.')[-1] == 'yaml':
            links.append(os.path.abspath(name))

    os.chdir(BASE_PATH)
    return links


def parse_markdown_for_home_page(post_datas, item_for_each_page):
    os.chdir('dist')
    os.mkdir('homePages')
    os.chdir('homePages')

    total_item = len(post_datas)
    page_total = math.ceil(total_item/item_for_each_page)

    with open('total_number.txt', 'w+') as f:
        page_total = str(page_total)
        f.write(page_total)

    # 按顺序写入json文件
    count = 1
    post_datas_copy = post_datas.copy()  # 下面的操作不够优雅会操作数组，可以求模来循环改代码就留着下次吧，阿巴阿巴。
    while (post_datas_copy):
        with open('page_{}.json'.format(count), 'w') as f:
            json.dump(post_datas_copy[:item_for_each_page], f, indent=4,)
            post_datas_copy[:item_for_each_page] = []  # 清理被用过的元素
        count += 1

    os.chdir(BASE_PATH)


def parse_info_in_each_markdown_post(markdown_path_list, abstract_words_number_for_each_item):
    post_datas = []

    for path in markdown_path_list:
        basename = os.path.basename(path)
        with open(path, 'r') as f:
            # 读取全文，利用正则表达式获取yaml部分
            content = f.read()
            content = content.strip('')
            match = re.search(RE_RULER, content)
            result = match.group(0)
            yaml_content = result.strip('-\n')
            yaml_content_python_obj = yaml.load(yaml_content)

            # 通过yaml部分计算正文位置，读取正文，生成摘要
            main_text_start = len(result.encode('utf-8'))
            f.seek(main_text_start)
            main_text = f.read()
            words_for_main_text = len(main_text)
            abstract = main_text[:abstract_words_number_for_each_item]

            if len(abstract) < words_for_main_text:
                abstract += ' ......\n(点击查看更多)'
            yaml_content_python_obj['abstract'] = abstract

            # 调整date的格式，记录到post_data数组
            yaml_content_python_obj['date'] = yaml_content_python_obj['date'].strftime(
                "%Y-%m-%d")
            # 加入basename
            yaml_content_python_obj['basename'] = basename
            post_datas.append(yaml_content_python_obj)
    # 按时间给数组排序
    post_datas = sorted(
        post_datas, key=lambda post: post['date'], reverse=True)
    return post_datas


def parse_markdown_for_tags_page(post_datas, item_for_each_page):
    """
    tags_dic{
        'tag1':[{post_1},{post_2},{post_3}]
    }
    """
    os.chdir('dist')
    os.mkdir('tags')
    os.chdir('tags')
    base_work_path = os.getcwd()

    tags_dic = {}
    # 依据tags分类
    for post in post_datas:
        tags = post['tags']
        for tag in tags:
            keys = tags_dic.keys()
            if tag in keys:
                tags_dic[tag].append(post)
            else:
                tags_dic[tag] = []
                tags_dic[tag].append(post)

    with open('tags_list.json', 'w') as f:
        tags_list = []
        for tag in tags_dic.keys():
            tags_list.append(
                {
                    'name': tag,
                    'number': len(tags_dic[tag])
                })
        json.dump(tags_list, f)

    for tag in tags_dic.keys():
        os.mkdir(tag)
        os.chdir(tag)
        total_item = len(tags_dic[tag])
        page_total = math.ceil(total_item/item_for_each_page)
        with open('total_number.txt', 'w+') as f:
            page_total = str(page_total)
            f.write(page_total)

        count = 1
        data_copy_list = tags_dic[tag].copy()  # 好像可以不用copy，下次优化
        while (data_copy_list):
            with open('page_{}.json'.format(count), 'w') as f:
                json.dump(
                    data_copy_list[:item_for_each_page], f, indent=4,)
                data_copy_list[:item_for_each_page] = []  # 清理被用过的元素
            count += 1
        os.chdir(base_work_path)
    os.chdir(BASE_PATH)


def parase_friend_links(links_path_list: list):
    link_datas = []

    os.mkdir('./dist/links')
    os.chdir('./dist/links')

    # 解析yaml文件（这里假设say中的文件存在）
    for path in links_path_list:
        with open(path, 'r') as f:
            yaml_content_python_obj = yaml.load(f.read())
            link_datas.append(yaml_content_python_obj)
    # 分类
    top_and_say_list = []
    top_non_say_list = []
    other_list = []
    for link in link_datas:
        if link['top'] == True:
            if link['say']:
                top_and_say_list.append(link)
            else:
                top_non_say_list.append(link)
        else:
            other_list.append(link)
    link_datas = top_and_say_list+top_non_say_list+other_list  # 一个简单的排序

    # 分页信息
    total_item = len(link_datas)
    if len(top_and_say_list) > 6:
        item_for_each_page = len(top_and_say_list)
    else:
        item_for_each_page = 6
    page_total = math.ceil(total_item/item_for_each_page)

    with open('total_number.txt', 'w+') as f:
        page_total = str(page_total)
        f.write(page_total)

    # 写入json
    count = 1
    while(link_datas):  # 用完就丢
        with open('page_{}.json'.format(count), 'w') as f:
            json.dump(link_datas[:item_for_each_page], f, indent=4,)
            link_datas[:item_for_each_page] = []  # 清理被用过的元素
        count += 1
    os.chdir(BASE_PATH)


def generate_normal_posts_for_dist(markdown_path_list):
    os.mkdir('./dist/posts')
    os.chdir('dist/posts')

    for path in markdown_path_list:
        basename = os.path.basename(path)
        with open(path, 'r') as f:
            # 读取全文，利用正则表达式获取yaml部分
            content = f.read()
            content = content.strip('')
            match = re.search(RE_RULER, content)
            result = match.group(0)

            # 通过yaml部分计算正文位置，读取正文
            main_text_start = len(result.encode('utf-8'))
            f.seek(main_text_start)
            main_text = f.read()
            with open(basename, 'w') as f1:
                f1.write(main_text)
    os.chdir(BASE_PATH)


def move_links_posts():
    os.chdir('links')
    files = os.listdir()
    posts_path = []
    for name in files:
        if name.split('.')[-1] == 'md':
            posts_path.append(os.path.abspath(name))
    os.chdir(BASE_PATH)

    os.chdir('./dist/posts')
    for path in posts_path:
        shutil.copy(path, '.')
    os.chdir(BASE_PATH)


def main():
    init()
    markdown_path = get_all_md()
    post_datas = parse_info_in_each_markdown_post(
        markdown_path, abstract_words_number_for_each_item=50)

    # 解析生成home和tags页面的数据
    parse_markdown_for_home_page(
        post_datas, item_for_each_page=6)
    parse_markdown_for_tags_page(post_datas, item_for_each_page=6)

    # 生成没有yaml的文章（可以优化，我们一边解析一边生成文章 - - 就是代码可能会变得混乱）
    generate_normal_posts_for_dist(markdown_path)
    # 解析links
    links_path = get_all_friend_links()
    parase_friend_links(links_path)

    # 移动文章
    move_links_posts()


main()
