import time

import certifi
import urllib3

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'
MODERN = time.strptime('2013-10-25T13:00:00+00:00', TIME_FORMAT)
LEGACY = time.strptime('2011-09-18T22:00:00+00:00', TIME_FORMAT)
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
