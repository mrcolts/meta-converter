import json
import urllib3
import time

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'
MODERN_TIME = time.strptime('2013-10-25T13:00:00+00:00', TIME_FORMAT)
LEGACY_TIME = time.strptime('2011-09-18T22:00:00+00:00', TIME_FORMAT)
OFFICIAL_MANIFEST = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
COMMUNITY_MANIFEST = './community_versions_manifest.json'
OUTPUT_MANIFEST = './manifest.json'
HEADERS = {"Host":"launchermeta.mojang.com", "User-Agent":"Mozilla/5.0"}

http = urllib3.PoolManager(headers=HEADERS)

def load_manifests():
    response = http.request("GET", OFFICIAL_MANIFEST)
    original = json.loads(response.data.decode("utf-8"))
    community = json.load(open(COMMUNITY_MANIFEST))
    return original, community

def dump_manifest(manifest):
    json.dump(manifest, open(OUTPUT_MANIFEST, "w+"))

def main():
    original, community = load_manifests()

    manifest = []

    for o_entry in original["versions"]:
        release_time = time.strptime(o_entry["releaseTime"], TIME_FORMAT)

        new_type = "modern" if release_time > MODERN_TIME else "legacy" if release_time > LEGACY_TIME else "classic"

        manifest.append({
            "id":       o_entry["id"],
            "vendor":   "official",
            "type":     new_type,
            "subtype":  o_entry["type"],
            "i18nKey":  f"misc.version.{new_type}.{o_entry['type']}",
            "url":      o_entry["url"]
        })

        marked_to_pop = []

        for c_entry in community:
            if c_entry["id"] == o_entry["id"]:
                manifest.append(c_entry)
                marked_to_pop.append(community.index(c_entry))

        for i in marked_to_pop:
            community.pop(i)

    dump_manifest(manifest)   

if __name__ == "__main__":
    main()
