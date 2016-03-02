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

