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
_get_or_bust = logic.get_or_bust
@toolkit.side_effect_free
def dataset_list(context, data_dict=None):
    '''
    '''
    data_dict["facet.field"] = ["organization", "tags", "res_format", "license_id"]
    result = logic.get_action("package_search")(context, data_dict)
    for i in range(len(result["results"])):
        
        try:
        	result["results"][i].pop("author_email")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("maintainer")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("relationships_as_object")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("private")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("maintainer_email")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("state")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("version")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("spatial")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("creator_user_id")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("type")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("tracking_summary")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("groups")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("relationships_as_subject")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("isopen")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("url")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"].pop("description")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"].pop("created")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"]["name"] = result["results"][i]["organization"].pop("title")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"].pop("revision_timestamp")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"].pop("is_organization")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"].pop("state")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"].pop("image_url")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"].pop("revision_id")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"].pop("type")
        except KeyError:
        	pass
        try:
        	result["results"][i]["organization"].pop("approval_status")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("name")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("notes")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("owner_org")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("license_url")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("revision_timestamp")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("license_id")
        except KeyError:
        	pass
        try:
        	result["results"][i].pop("revision_id")
        except KeyError:
        	pass
        try:
        	result["results"][i]["num_tags"] = len(result["results"][i]["tags"])
        except KeyError:
        	pass
        tags = []
        for j in range(len(result["results"][i]["tags"])):
        	tags.append(result["results"][i]["tags"][j].pop("display_name"))

        res_type = set()
        for j in range(len(result["results"][i]["resources"])):
        	res_type.add(result["results"][i]["resources"][j].pop("format"))

        try:
            result["results"][i]["publish_date"] = result["results"][i]["publish_date"]
        except KeyError:
            result["results"][i]["publish_date"] = None
        result["results"][i].pop("resources")
        result["results"][i]["resource_type"] = [x for x in res_type]

        result["results"][i]["tags"] = tags


        result["results"][i]["display_name"] = result["results"][i].pop("title")

        author = model.Session.query(model.User).filter(model.User.id == result["results"][i]["author"]).first()
        if author != None:
            result["results"][i]["author"] = author.display_name
    result["facets"] = result["search_facets"]
    result.pop("search_facets")
    return result

@toolkit.side_effect_free
def package_show(context, data_dict=None):
    dd = {'id':_get_or_bust(data_dict, 'id')}
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
        try:
            if(all_data["display_name"] == "" or all_data["display_name"] == None):
                all_data["display_name"] = all_data.pop("title")
        except KeyError:
            all_data["display_name"] = all_data.pop("title")
            pass
    except KeyError:
            pass
    for i in range(len(all_data["resources"])):
        try:
            all_data["resources"][i].pop("resource_group_id")
        except KeyError:
            pass
        try:
            all_data["resources"][i].pop("last_modified")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("data_correctness")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("maintainer")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("periodicity")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("cache_last_updated")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("revision_timestamp")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("webstore_last_updated")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("datastore_active")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("valid_from")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("size")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("state")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("transformed")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("schema")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("status")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("periodicity_description")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("hash")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("validity")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("tracking_summary")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("revision_id")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("url_type")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("active_to")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("data_correctness_description")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("validity_description")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("mimetype")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("cache_url")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("valid_to")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("webstore_url")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("mimetype_inner")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("position")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("active_from")
        except KeyError:
            pass
        try:    
            all_data["resources"][i].pop("resource_type")
        except KeyError:
            pass
        try:    
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
    
    try:
        all_data["organization"].pop("created")
    except KeyError:
        pass
    try:    
        all_data["organization"]["name"] = all_data["organization"]["title"]
    except KeyError:
        pass
    try:    
        all_data["organization"].pop("revision_timestamp")
    except KeyError:
        pass
    try:    
        all_data["organization"].pop("is_organization")
    except KeyError:
        pass
    try:    
        all_data["organization"].pop("state")
    except KeyError:
        pass
    try:    
        all_data["organization"].pop("state")
    except KeyError:
        pass
    try:    
        all_data["organization"].pop("image_url")
    except KeyError:
        pass
    try:    
        all_data["organization"].pop("revision_id")
    except KeyError:
        pass
    try:    
        all_data["organization"].pop("type")
    except KeyError:
        pass
    try:    
        all_data["organization"].pop("approval_status")
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
