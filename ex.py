# vim:ts=4 sw=4 expandtab softtabstop=4
import json
import jsonmerge
import jsonschema
import pprint
import sys

def main():
    record = json.load(open("blank-ocds.json"))
    record_schema = json.load(open("../standard/standard/schema/record-schema.json"))
    jsonschema.validate(record, record_schema)

    merger_schema = {
            'id': "file:///home/avian/dev/opencontracting/standard/standard/schema/merge-schema.jsom",
            '$ref': "release-schema.json#/definitions/release"
    }
    merger = jsonmerge.Merger(merger_schema)

    base = None
    for i, release in enumerate(record['records'][0]['releases']):

        jsonschema.validate(release, merger_schema)

        release_meta = release.pop("releaseMeta")

        base = merger.merge(base, release, meta=release_meta)

        f = open("out%02d.json" % (i,), "w")
        json.dump(base, f, indent=4, sort_keys=True)

main()
