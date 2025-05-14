import requests
import time
import json
import re

home_dir = os.path.expanduser("~")
snyk_token = json.load(open(home_dir + "/secret.json", "r"))["snyk"]

if __name__ == '__main__':
    cve_list = json.load(open("../../NVD/cve_list.json", "r"))
    package2snykID = {}
    linecount = 0
    t1 = time.time()

    headers = {
    "Authorization": f"token {snyk_token}",
    "Content-Type": "application/json"  # 如果需要 JSON 数据，可以添加
}
    for each_cve in cve_list:
        if linecount % 100 == 0:
            print(linecount, time.time() - t1)
        linecount += 1
        if linecount % 100 == 0:
            json.dump(package2snykID, open("../../snyk/package2snykID.json", "w"))
        for package in ["unmanaged", "maven", "npm", "pip", "go"]:
            search_url = f"https://security.snyk.io/vuln/{package}?search={each_cve}"
            response = requests.get(search_url, headers=headers)
            time.sleep(0.05)
            if response.status_code == 200:
                snyk_urls = re.findall(r'vuln/SNYK-[^"\']+', response.text)
                if len(snyk_urls) > 0:
                    package2snykID.setdefault(package, [])
                    package2snykID[package] = package2snykID[package] + snyk_urls
                    break
            elif response.status_code in [403, 404, 429]:
                print("request mistake")


        

