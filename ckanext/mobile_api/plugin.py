import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.logic
import ckan.model as model
from ckan.common import _, c


import mobile_api

class MobileApi(plugins.SingletonPlugin):
    ''' '''
    plugins.implements(plugins.interfaces.IActions)
    def get_actions(self):
        return {'m_package_search':mobile_api.dataset_list,
                'm_package_show':mobile_api.package_show}
