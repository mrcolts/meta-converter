import json
import threading
from queue import Queue

from settings import *


def convert_meta(url):
    meta: dict = json.loads(http.request("GET", url).data.decode("utf-8"))

    output = {
        "id": meta["id"],
        "type": meta["type"],
        "client": meta["downloads"]["client"]["url"],
        "assets": {
            "id": meta["assetIndex"]["id"],
            "url": meta["assetIndex"]["url"]
        },
        "arguments": [
            "-Xmx${memory}M",
            "-Djava.library.path=${natives_path}",
            "-Dfile.encoding=UTF-8",
            "-cp",
            "${classpath}",
            meta["mainClass"]
        ],
        "libraries": [],
        "natives": {}
    }

    if "arguments" in meta.keys():
        output["arguments"].extend([x for x in meta["arguments"]["game"] if "rules" not in x])
    else:
        output["arguments"].extend([x for x in meta["minecraftArguments"].split(" ")])

    for lib in meta["libraries"]:
        if "classifiers" in lib["downloads"]:
            for key, value in lib["downloads"]["classifiers"].items():
                if key == "javadoc" or key == "sources":
                    continue
                elif key == "natives-osx":
                    key = "natives-macos"

                if key not in output["natives"]:
                    output["natives"][key] = []

                output["natives"][key].append(value["path"])
        else:
            output["libraries"].append(lib["downloads"]["artifact"]["path"])

    json.dump(output, open(OUTPUT_META.format(meta["type"], meta["id"]), "w+"))


class Downloader(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url = self.queue.get()
            convert_meta(url)
            self.queue.task_done()


def load_manifests():
    response = http.request("GET", OFFICIAL_MANIFEST)
    original = json.loads(response.data.decode("utf-8"))
    community = json.load(open(COMMUNITY_MANIFEST))
    return original, community


def main():
    queue = Queue()

    for _ in range(10):
        t = Downloader(queue)
        t.setDaemon(True)
        t.start()

    original, community = load_manifests()

    output = []

    for o_entry in original["versions"]:
        release_time = time.strptime(o_entry["releaseTime"], TIME_FORMAT)

        group = "modern" if release_time > MODERN else "legacy" if release_time > LEGACY else "classic"

        output.append({
            "id": o_entry["id"],
            "vendor": "official",
            "group": group,
            "type": o_entry["type"],
            "url": BASE_URL.format(o_entry["type"], o_entry["id"])
        })

        marked_to_pop = []

        for c_entry in community:
            if c_entry["id"] == o_entry["id"]:
                output.append(c_entry)
                marked_to_pop.append(community.index(c_entry))

        for i in marked_to_pop:
            community.pop(i)

        queue.put(o_entry["url"])

    json.dump(output, open(OUTPUT_MANIFEST, "w+"))
    queue.join()


if __name__ == "__main__":
    main()
