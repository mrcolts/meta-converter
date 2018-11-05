import json

import time

import certifi
import urllib3

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'
MODERN_ENDPOINT = time.strptime('2013-10-25T13:00:00+00:00', TIME_FORMAT)
LEGACY_ENDPOINT = time.strptime('2011-09-18T22:00:00+00:00', TIME_FORMAT)
OFFICIAL_MANIFEST = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
COMMUNITY_MANIFEST = './community_versions_manifest.json'
OUTPUT_MANIFEST = './manifest.json'
OUTPUT_META = './meta/{}_{}.json'
HEADERS = {"Host": "launchermeta.mojang.com", "User-Agent": "Mozilla/5.0"}
BASE_URL = 'http://localhost/{}_{}.json'

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where(),
    headers=HEADERS
)


def load_manifests():
    response = http.request("GET", OFFICIAL_MANIFEST)
    original = json.loads(response.data.decode("utf-8"))
    community = json.load(open(COMMUNITY_MANIFEST))
    return original, community


def convert_meta(url):
    meta: dict = json.loads(http.request("GET", url).data.decode("utf-8"))

    output = {
        "client": meta["downloads"]["client"]["url"],
        "mainClass": meta["mainClass"],
    }

    if "arguments" in meta.keys():
        output["arguments"] = [x for x in meta["arguments"]["game"] if "rules" not in x]
    else:
        output["arguments"] = [x for x in meta["minecraftArguments"].split(" ")]

    output["assets"] = {
        "id": meta["assetIndex"]["id"],
        "url": meta["assetIndex"]["url"]
    }

    libraries = []
    natives = []

    for lib in meta["libraries"]:
        if "classifiers" in lib["downloads"]:
            native = {}
            for key, value in lib["natives"].items():
                raw_native = lib["downloads"]["classifiers"][value]
                native[key] = {
                    "path": raw_native["path"],
                    "url": raw_native["url"]
                }
            natives.append(native)
        else:
            raw_lib = lib["downloads"]["artifact"]
            libraries.append({
                "path": raw_lib["path"],
                "url": raw_lib["url"]
            })

    output["libraries"] = libraries
    output["natives"] = natives

    json.dump(output, open(OUTPUT_META.format(meta["type"], meta["id"]), "w+"))


def main():
    original, community = load_manifests()

    manifest = []

    for o_entry in original["versions"]:
        release_time = time.strptime(o_entry["releaseTime"], TIME_FORMAT)

        new_type = "modern" if release_time > MODERN_ENDPOINT else "legacy" if release_time > LEGACY_ENDPOINT else "classic"

        manifest.append({
            "id": o_entry["id"],
            "vendor": "official",
            "type": new_type,
            "subtype": o_entry["type"],
            "url": BASE_URL.format(o_entry["type"], o_entry["id"])
        })

        marked_to_pop = []

        for c_entry in community:
            if c_entry["id"] == o_entry["id"]:
                manifest.append(c_entry)
                marked_to_pop.append(community.index(c_entry))

        for i in marked_to_pop:
            community.pop(i)

        convert_meta(o_entry["url"])

    json.dump(manifest, open(OUTPUT_MANIFEST, "w+"))


if __name__ == "__main__":
    main()
