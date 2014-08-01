# vim:ts=4 sw=4 expandtab softtabstop=4
import json
import jsonmerge
import jsonschema
import pprint
import sys
import urllib

def main():
    # Load a record JSON
    record = json.load(open("blank-ocds.json"))

    # Validate it against a record schema
    root = "https://raw.githubusercontent.com/avian2/ocds-standard/add-merge-strategies/standard/schema"
    f = urllib.urlopen(root + "/record-schema.json")
    record_schema = json.load(f)

    jsonschema.validate(record, record_schema)

    # Our record JSON contains a list that contains objects, conforming
    # to the part of the release schema. Since we don't have a stand-alone
    # schema file describing those parts, we make a shim here that just
    # references the correct part of the release schema.
    merger_schema = {
        'id': root + "/merge-schema.json",
        '$ref': "release-schema.json#/definitions/release"
    }
    merger = jsonmerge.Merger(merger_schema)

    # We do a similar thing to describe the metadata that we use to describe
    # each release.
    meta_schema = {
        'id': root + "/meta-schema.json",
        '$ref': "release-schema.json#/definitions/release/definitions/releaseMeta"
    }

    # Generate a schema for the document, resulting from the merge operation,
    # and save it to a file for later inspection.
    merged_schema = merger.get_schema(meta=meta_schema)
    f = open("outschema.json", "w")
    json.dump(merged_schema, f, indent=4, sort_keys=True)

    # Start with an empty base document...
    base = None

    # Iterate through all the releases in the record...
    for i, release in enumerate(record['records'][0]['releases']):

        # first validate the release to make sure it complies with the schema.
        jsonschema.validate(release, merger_schema)

        # we could remove "releaseMeta" from the release structure here to avoid duplication, but
        # then the structure doesn't validate against release-schema.json
        release_meta = release["releaseMeta"]

        # merge each release consecutively into the base document, using the
        # shim we made above.
        base = merger.merge(base, release, meta=release_meta)

        # check if the resulting document validates against the merged schema
        # (a validation error here means a bug in jsonmerge)
        jsonschema.validate(base, merged_schema)

        # write out each step into a file for inspection.
        f = open("out%02d.json" % (i,), "w")
        json.dump(base, f, indent=4, sort_keys=True)

main()
