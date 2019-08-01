# -*- coding: utf-8 -*-

from flask import current_app


def add_to_index(index, model):
    """
    将 model 数据加入 es 索引
    如果你尝试添加一个带有现有id的条目，那么Elasticsearch会用新的条目替换旧条目，
    所以add_to_index()可以用于新建和修改对象。
    :param index:
    :param model:
    :return:
    """
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id,
                                    body=payload)


def remove_from_index(index, model):
    """
    从 es 索引中删除 model 相关数据
    :param index:
    :param model:
    :return:
    """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, page, per_page):
    """
    查询
    :param index:
    :param query:
    :param page:
    :param per_page:
    :return:
    """
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        # doc_type=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']

# 为了保持数据清洁 在test之后进行索引的删除
# app.elasticsearch.indices.delete('posts')
