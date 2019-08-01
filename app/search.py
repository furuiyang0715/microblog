# -*- coding: utf-8 -*-

from flask import current_app


def add_to_index(index, model):
    if current_app.elasticsearch:
        # 优先使用 es 搜索
        payload = dict()
        for field in model.__searchable__:
            payload[field] = getattr(model, field)
        current_app.elasticsearch.index(index=index, doc_type=index, id=model.id,
                                        body=payload)
    # elif current_app.whoosh:
    #     pass

    else:
        return


def remove_from_index(index, model):
    """
    从 es 索引中删除 model 相关数据
    :param index:
    :param model:
    :return:
    """
    if current_app.elasticsearch:
        current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)

    # elif current_app.whoosh:
    #     pass

    else:
        return


def query_index(index, query, page, per_page):
    """
    查询
    :param index:
    :param query:
    :param page:
    :param per_page:
    :return:
    """
    if current_app.elasticsearch:
        search = current_app.elasticsearch.search(
            index=index,
            # doc_type=index,
            body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
                  'from': (page - 1) * per_page, 'size': per_page})
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        return ids, search['hits']['total']

    elif current_app.whoosh:
        pass

    # else:
    #     return [], 0


# test
# app.elasticsearch.indices.delete('posts')
