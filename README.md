# ckanext-mobile_api

minimal json for mobile applications
```json
{
  help: " ",
  success: true,
  result: {
  count: 863,
  sort: "metadata_modified desc",
  facets: {
          organization: [
                        "org1",
                        "org2",
                        ],
          res_format: [
                      "xml",
                      "xlsx",
                      "xls"
                      ],
          tags: [
                "tag1",
                "tag2"
                ]
        },
results: [
        {
        organization: {
                      name: "xz",
                      id: "id"
                      },
        display_name: "zzz",
        id: "id",
        resources: [

        {
          id: "id",
          format: "format",
          name: "display name",
          description: "description"
          url: "url"
        }
      ]
    }
],
search_facets: { }
}
}
```

###params:
+ q (string) – the solr query. Optional. Default: “*:*”
+ fq (string) – any filter queries to apply. Note: +site_id:{ckan_site_id} is added to this string prior to the query being executed.
+ sort (string) – sorting of the search results. Optional. Default: ‘relevance asc, metadata_modified desc’. As per the solr documentation, this is a comma-separated string of field names and sort-orderings.
+ rows (int) – the number of matching rows to return.
+ start (int) – the offset in the complete result for where the set of returned datasets should begin.

###how to use:
+ ckan_base_url/api/3/action/m_package_search
+ facets: ckan_base_url/api/3/action/m_package_search?fq=facet_name:value (tags, organization, res_format)

###m_package_show
```json
{
  help: null,
  success: true,
  result: {
          license_title: "Creative Commons Non-Commercial (Any)",
          id: "id",
          metadata_created: "2016-01-19T12:14:59.412134",
          metadata_modified: "2016-03-04T13:04:59.018864",
          author: "xxx",
          resources: [
                    {
                    id: "xxx",
                    description: "xxx",
                    format: "CSV",
                    last_modified: "2016-03-04T14:03:42.550208",
                    name: "xxx",
                    created: "2016-01-19T13:18:20.434992",
                    url: "xxx"
                    }
                    ],
          num_resources: 1,
          tags: [
                    {
                    display_name: "xxx",
                    name: "xxx",
                    id: "xxx"
                    }
              ],
          license_id: "xxx",
          num_tags: 1,
          organization: {
          description: "xxx",
          created: "2015-12-18T14:52:14.771756",
          title: "xxx",
          name: "xxx",
          revision_timestamp: "2015-12-18T13:52:14.681868",
          is_organization: true,
          state: "active",
          image_url: "xxx",
          revision_id: "xxx",
          id: "xxx",
          approval_status: "xxx"
          },
          name: "xxx",
          notes: "xxx",
          publish_date: "2016-01-19",
          title: "xxx"
          }
}
```
##parameters:
+ id (dataset id)
