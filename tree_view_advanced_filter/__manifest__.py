# -*- coding: utf-8 -*-
# Part of Aktiv Software 2021-Today.
{
    'name': 'Tree View Advanced Search / Direct Filter in List',
    'version': '15.0.1.0.4',
    'category': 'Advanced search on Tree view',
    'summary': """This module allows a user to directly filter on the Tree / List View.
    The data will be filtered Runtime.
    List Filter ,
    Filter List,
    Column Filter,
    Tree Filter,
    Filter Tree,
    Advance Search,
    Search Advance,
    Tree Search,
    Direct Search,
    Fast Search,
    Quick Search,
    Dynamic Search,
    Dynamic Tree,
    Data Search,
    Search Data,
    Data search in Tree
    """,
    'description': """
        This module allows a user to directly filter on the Tree / List View.
    The data will be filtered Runtime. Columns can be directly searched on the Tree View.
    List Filter
    Column Filter
    Tree Filter
    Advance Search
    Tree Search
    Direct Search
    Fast Search
    Quick Search
    Dynamic Search
    Dynamic Tree
    Data Search
    Data search in Tree
    """,
    'author': 'Aktiv Software',
    'website': 'http://www.aktivsoftware.com',
    'license': 'OPL-1',
    'price': 69.00,
    'currency': "EUR",
    'depends': ['web'],
    'data': [],
    'assets': {
            'web.assets_backend': [
                # custum Library
                'tree_view_advanced_filter/static/src/js/tree.js',
                'tree_view_advanced_filter/static/src/js/custom_list_view_manager_controller.js',
                'tree_view_advanced_filter/static/src/css/main.css',
                # External Library
                'https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.min.js',
                'https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.css',
            ],
        },

    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
