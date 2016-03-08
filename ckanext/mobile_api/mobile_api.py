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
from ckan.common import _, g, c
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
import ckan.model as model

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
    for item in plugins.PluginImplementations(plugins.IPackageController):
        data_dict = item.before_search(data_dict)
    abort = data_dict.get('abort_search', False)

    if data_dict.get('sort') in (None, 'rank'):
        data_dict['sort'] = 'metadata_modified desc'

    results = []
    if not abort:
        data_source = 'data_dict' if data_dict.get('use_default_schema',
            False) else 'validated_data_dict'
        data_dict['fl'] = 'id {0}'.format(data_source)
        fq = data_dict.get('fq', '')
        if not context.get('ignore_capacity_check', False):
            fq = ' '.join(p for p in fq.split(' ')
                            if not 'capacity:' in p)
            data_dict['fq'] = fq + ' capacity:"public"'
        extras = data_dict.pop('extras', None)

        query = search.query_for(model.Package)
        query.run(data_dict)
        data_dict['extras'] = extras

        for package in query.results:
            package, package_dict = package['id'], package.get(data_source)
            pkg_query = session.query(model.PackageRevision)\
                .filter(model.PackageRevision.id == package)\
                .filter(_and_(
                    model.PackageRevision.state == u'active',
                    model.PackageRevision.current == True
                ))
            pkg = pkg_query.first()
            if not pkg:
                log.warning('package %s in index but not in database' % package)
                continue
            if package_dict:
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
    for item in plugins.PluginImplementations(plugins.IPackageController):
        search_results = item.after_search(search_results,data_dict)
    for facet in search_results['search_facets']:
        search_results['search_facets'][facet]['items'] = sorted(
                search_results['search_facets'][facet]['items'],
                key=lambda facet: facet['display_name'], reverse=True)
    result = []
    facets__ = {}
    o_list = logic.get_action('organization_list')(context,{})
    #full_org_data = [ logic.get_action("organization_show")(context, {"id":x}) for x in o_list]
    full_org_data = [ model.Session.query(model.Group).filter(model.Group.name == x).first()  for x in o_list]
    #facets__['organization']= [{"display_name":x["display_name"], "id":x["id"]} for x in full_org_data ]
    facets__['organization']= [{"display_name":x.display_name, "id":x.id} for x in full_org_data ]

    facets__['tags'] = logic.get_action('tag_list')(context,{})
    formats = set()
    license_type = []
    all_license_types = logic.get_action("license_list")(context, {})
    for license in all_license_types:
        license_type.append({"title":license["title"], "id":license["id"]})
    for i in 'abcdefghijklmnopqrstuvwxyz':
        for j in logic.get_action('format_autocomplete')(context, {'q':i}):
            formats.add(j)
    facets__['res_format'] = [x for x in formats]
    facets__['license_type'] = [x for x in license_type]      
    facet_titles = [('organization', u'Organiz\xe1cie'), ('tags', u'Tagy'), ('res_format', u'Form\xe1ty'), ('license_id', u'Licencia')]
    context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}
    data_dict = {
        'q': '*:*',
        'facet.field': g.facets,
        'rows': 4,
        'start': 0,
        'sort': 'views_recent desc',
        'fq': 'capacity:"public"'
    }
    query = logic.get_action('package_search')(
        context, data_dict)

    search_results['facets'] =  query['search_facets'] #facets__
    search_results['facets'].pop('groups')
    for dataset in search_results['results']:
        helper = {}
        helper['display_name'] = dataset['title']
        helper['id'] = dataset['id']
        helper['organization'] = {'name':dataset['organization']['title'], 'id':dataset['organization']['id']}
        #helper['resources'] = [{'name':x['name'], 'description':x['description'], 'format':x['format'], 'id':x['id'], 'url':x['url']} for x in dataset['resources']]
        helper['resource_type'] = [x for x in set([ x['format'] for x in dataset['resources']])]
        helper['tags'] = [x["display_name"] for x in dataset['tags']]
        helper["metadata_created"] = dataset["metadata_created"]
        try:
            helper["publish_date"] = dataset["publish_date"]
        except KeyError:
            helper["publish_date"] = None
        helper["metadata_modified"] = dataset["metadata_modified"]
        helper["num_resources"] = len(dataset["resources"])
        helper["license_title"] = dataset["license_title"]
        author = model.Session.query(model.User).filter(model.User.id == dataset["author"]).first()
        if author == None:
            helper["author"] =dataset["author"]
        else:
            helper["author"] = author.display_name

        result.append(helper)
    search_results['results'] = result
    return search_results

@toolkit.side_effect_free
def package_show(context, data_dict=None):
    dd = {'id':data_dict['id']}
    all_data = logic.get_action("package_show")(context,dd)
    author = model.Session.query(model.User).filter(model.User.id == all_data["author"]).first()
    if author == None:
        all_data['author'] =all_data["author"]
    else:
        all_data['author'] = author.display_name
    try:
        all_data.pop("maintainer")
        all_data.pop("relationships_as_object")
        all_data.pop("private")
        all_data.pop("maintainer_email")
        all_data.pop("revision_timestamp")
        all_data.pop("author_email")
        all_data.pop("state")
        all_data.pop("version")
        all_data.pop("spatial")
        all_data.pop("creator_user_id")
        all_data.pop("type")
        all_data.pop("tracking_summary")
        all_data.pop("groups")
        all_data.pop("relationships_as_subject")
        all_data.pop("isopen")
        all_data.pop("url")
        all_data.pop("owner_org")
        all_data.pop("license_url")
        all_data.pop("revision_id")
        all_data["display_name"] = all_data.pop("title")
    except KeyError:
            pass
    for i in range(len(all_data["resources"])):
        try:
            all_data["resources"][i].pop("resource_group_id")
            all_data["resources"][i].pop("data_correctness")
            all_data["resources"][i].pop("maintainer")
            all_data["resources"][i].pop("periodicity")
            all_data["resources"][i].pop("cache_last_updated")
            all_data["resources"][i].pop("revision_timestamp")
            all_data["resources"][i].pop("webstore_last_updated")
            all_data["resources"][i].pop("datastore_active")
            all_data["resources"][i].pop("valid_from")
            all_data["resources"][i].pop("size")
            all_data["resources"][i].pop("state")
            all_data["resources"][i].pop("transformed")
            all_data["resources"][i].pop("schema")
            all_data["resources"][i].pop("status")
            all_data["resources"][i].pop("periodicity_description")
            all_data["resources"][i].pop("hash")
            all_data["resources"][i].pop("validity")
            all_data["resources"][i].pop("tracking_summary")
            all_data["resources"][i].pop("revision_id")
            all_data["resources"][i].pop("url_type")
            all_data["resources"][i].pop("active_to")
            all_data["resources"][i].pop("data_correctness_description")
            all_data["resources"][i].pop("validity_description")
            all_data["resources"][i].pop("mimetype")
            all_data["resources"][i].pop("cache_url")
            all_data["resources"][i].pop("valid_to")
            all_data["resources"][i].pop("webstore_url")
            all_data["resources"][i].pop("mimetype_inner")
            all_data["resources"][i].pop("position")
            all_data["resources"][i].pop("active_from")
            all_data["resources"][i].pop("resource_type")
            all_data["resources"][i].pop("license_id")
        except KeyError:
            pass
    for i in range(len(all_data["tags"])):
        try:
            all_data["tags"][i].pop("vocabulary_id")
            #all_data["tags"][i].pop("name")
            all_data["tags"][i].pop("revision_timestamp")
            #all_data["tags"][i].pop("id")
            all_data["tags"][i].pop("state")
        except KeyError:
            pass
    for i in range(len(all_data["organization"])):
        try:
            all_data["organization"][i].pop("created")
            all_data["organization"][i].pop("name")
            all_data["organization"][i].pop("revision_timestamp")
            all_data["organization"][i].pop("is_organization")
            all_data["organization"][i].pop("state")
            all_data["organization"][i].pop("state")
            all_data["organization"][i].pop("image_url")
            all_data["organization"][i].pop("revision_id")
            all_data["organization"][i].pop("type")
            all_data["organization"][i].pop("approval_status")
        except KeyError:
            pass

    return all_data

@toolkit.side_effect_free
def m_organization_list(context, data_dict=None):
    org_list = logic.get_action("organization_list")(context, data_dict)
    result = []
    logging.warning(org_list)
    result = [logic.get_action("organization_show")(context, {'id':x, "include_datasets":False}) for x in org_list ]
    logging.warning(result)
    for i in range(len(result)):
        try:
            result[i].pop("users")
            result[i].pop("approval_status")
            result[i].pop("state")
            result[i].pop("revision_id")
            result[i].pop("groups")
            result[i].pop("type")
            result[i].pop("tags")
            result[i].pop("name")
            result[i].pop("display_name")
            result[i].pop("is_organization")
            result[i].pop("extras")
            result[i].pop("description")
            result[i].pop("image_display_url")
            result[i].pop("created")
        except KeyError:
            pass
    return result

@toolkit.side_effect_free
def m_organization_show(context, data_dict):
    data_dict['include_datasets'] = False
    result = logic.get_action("organization_show")(context, data_dict)
    try:
        result.pop("users")
        result.pop("image_display_url")
        result.pop("approval_status")
        result.pop("is_organization")
        result.pop("extras")
        result.pop("groups")
        result.pop("revision_id")
        result.pop("type")
        result.pop("tags")
        result.pop("name")

    except KeyError:
        pass

    return result
