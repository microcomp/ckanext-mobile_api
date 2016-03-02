import urllib

from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import uuid
import datetime
import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as df
import ckan.plugins as p
from ckan.common import _, c
import ckan.plugins.toolkit as toolkit
import urllib2
import logging
import ckan.logic
from pylons import config, request, response
import json

import socket

from pylons import config
import sqlalchemy

import ckan.lib.dictization
import ckan.logic.action
import ckan.logic.schema
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.navl.dictization_functions
import ckan.model as model
import ckan.model.misc as misc
import ckan.plugins as plugins
import ckan.lib.search as search
import ckan.lib.plugins as lib_plugins
import ckan.lib.activity_streams as activity_streams
import ckan.new_authz as new_authz

_validate = ckan.lib.navl.dictization_functions.validate
_table_dictize = ckan.lib.dictization.table_dictize
_check_access = logic.check_access
NotFound = logic.NotFound
ValidationError = logic.ValidationError
_get_or_bust = logic.get_or_bust

_select = sqlalchemy.sql.select
_aliased = sqlalchemy.orm.aliased
_or_ = sqlalchemy.or_
_and_ = sqlalchemy.and_
_func = sqlalchemy.func
_desc = sqlalchemy.desc
_case = sqlalchemy.case
_text = sqlalchemy.text
@toolkit.side_effect_free
def dataset_list(context, data_dict=None):
    '''
    '''
    # sometimes context['schema'] is None
    schema = (context.get('schema') or
              logic.schema.default_package_search_schema())
    data_dict, errors = _validate(data_dict, schema, context)
    data_dict.update(data_dict.get('__extras', {}))
    data_dict.pop('__extras', None)
    if errors:
        raise ValidationError(errors)

    model = context['model']
    session = context['session']

    _check_access('package_search', context, data_dict)

    data_dict['extras'] = data_dict.get('extras', {})
    for key in [key for key in data_dict.keys() if key.startswith('ext_')]:
        data_dict['extras'][key] = data_dict.pop(key)

    # check if some extension needs to modify the search params
    for item in plugins.PluginImplementations(plugins.IPackageController):
        data_dict = item.before_search(data_dict)

    # the extension may have decided that it is not necessary to perform
    # the query
    abort = data_dict.get('abort_search', False)

    if data_dict.get('sort') in (None, 'rank'):
        data_dict['sort'] = 'metadata_modified desc'

    results = []
    if not abort:
        data_source = 'data_dict' if data_dict.get('use_default_schema',
            False) else 'validated_data_dict'
        # return a list of package ids
        data_dict['fl'] = 'id {0}'.format(data_source)

        # If this query hasn't come from a controller that has set this flag
        # then we should remove any mention of capacity from the fq and
        # instead set it to only retrieve public datasets
        fq = data_dict.get('fq', '')
        if not context.get('ignore_capacity_check', False):
            fq = ' '.join(p for p in fq.split(' ')
                            if not 'capacity:' in p)
            data_dict['fq'] = fq + ' capacity:"public"'

        # Pop these ones as Solr does not need them
        extras = data_dict.pop('extras', None)

        query = search.query_for(model.Package)
        query.run(data_dict)

        # Add them back so extensions can use them on after_search
        data_dict['extras'] = extras

        for package in query.results:
            # get the package object
            package, package_dict = package['id'], package.get(data_source)
            pkg_query = session.query(model.PackageRevision)\
                .filter(model.PackageRevision.id == package)\
                .filter(_and_(
                    model.PackageRevision.state == u'active',
                    model.PackageRevision.current == True
                ))
            pkg = pkg_query.first()

            ## if the index has got a package that is not in ckan then
            ## ignore it.
            if not pkg:
                log.warning('package %s in index but not in database' % package)
                continue
            ## use data in search index if there
            if package_dict:
                ## the package_dict still needs translating when being viewed
                package_dict = json.loads(package_dict)
                if context.get('for_view'):
                    for item in plugins.PluginImplementations( plugins.IPackageController):
                        package_dict = item.before_view(package_dict)
                results.append(package_dict)
            else:
                results.append(model_dictize.package_dictize(pkg,context))

        count = query.count
        facets = query.facets
    else:
        count = 0
        facets = {}
        results = []

    search_results = {
        'count': count,
        'facets': facets,
        'results': results,
        'sort': data_dict['sort']
    }

    # Transform facets into a more useful data structure.
    restructured_facets = {}
    for key, value in facets.items():
        restructured_facets[key] = {
                'title': key,
                'items': []
                }
        for key_, value_ in value.items():
            new_facet_dict = {}
            new_facet_dict['name'] = key_
            if key in ('groups', 'organization'):
                group = model.Group.get(key_)
                if group:
                    new_facet_dict['display_name'] = group.display_name
                else:
                    new_facet_dict['display_name'] = key_
            elif key == 'license_id':
                license = model.Package.get_license_register().get(key_)
                if license:
                    new_facet_dict['display_name'] = license.title
                else:
                    new_facet_dict['display_name'] = key_
            else:
                new_facet_dict['display_name'] = key_
            new_facet_dict['count'] = value_
            restructured_facets[key]['items'].append(new_facet_dict)
    search_results['search_facets'] = restructured_facets

    # check if some extension needs to modify the search results
    for item in plugins.PluginImplementations(plugins.IPackageController):
        search_results = item.after_search(search_results,data_dict)

    # After extensions have had a chance to modify the facets, sort them by
    # display name.
    for facet in search_results['search_facets']:
        search_results['search_facets'][facet]['items'] = sorted(
                search_results['search_facets'][facet]['items'],
                key=lambda facet: facet['display_name'], reverse=True)
    result = []
    facets__ = {}
    facets__['organization'] = logic.get_action('organization_list')(context,{})
    facets__['tags'] = logic.get_action('tag_list')(context,{})
    formats = set()
    for i in 'abcdefghijklmnopqrstuvwxyz':
        for j in logic.get_action('format_autocomplete')(context, {'q':i}):
            formats.add(j)
    facets__['res_format'] = [x for x in formats]      
    #TODO --TAG and FORMATS
    search_results['facets'] = facets__
    for dataset in search_results['results']:
        helper = {}
        helper['display_name'] = dataset['title']
        helper['id'] = dataset['id']
        helper['organization'] = {'name':dataset['organization']['title'], 'id':dataset['organization']['id']}
        helper['resources'] = [{'name':x['name'], 'description':x['description'], 'format':x['format'], 'id':x['id'], 'url':x['url']} for x in dataset['resources']]
        result.append(helper)
    search_results['results'] = result
    return search_results

