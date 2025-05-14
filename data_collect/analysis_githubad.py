# get all repo with at least one patch in github AD
import json
from pathlib import Path

linecount = 0
cve2githubID = {}
for json_file in list(Path('../../advisory-database/advisories/github-reviewed/').rglob('*.json')):
    if linecount % 100 == 0:
        print(linecount)
    linecount += 1
    entry = json.load(open(json_file, "r"))
    if len(entry["aliases"]) == 0:
        continue
    cve = entry["aliases"][0]
    affected = entry["affected"]
    references = entry["references"]
    cve2githubID[cve] = entry["id"]


eco2cve2ref = json.load(open("../../advisory-database/eco2cve2reference.json", "r"))

repo2count = {}

for eco, cve2ref in eco2cve2ref.items():
    for cve, refs in cve2ref.items():
        for ref in refs:
            if "github.com/" in ref and "/commit/" in ref:
                repo = ref.split("/")[3] + "_" + ref.split("/")[4]
                repo2count.setdefault(eco + "@@@" + repo, set([]))
                repo2count[eco + "@@@" + repo].add(cve + "@@@" + ref)

sorted_repo2count = sorted(repo2count.items(), key = lambda x:len(x[1]), reverse=True)

fout = open("../../advisory-database/all_refs.csv", "w")
fout.write("eco,repo,cve,ref,url\n")
for eco_repo, ref_set in sorted_repo2count:
    eco, repo = eco_repo.split("@@@") 
    for cve_ref in ref_set:
        cve, ref = cve_ref.split("@@@")
        fout.write(eco + "," + repo + "," + cve + "," + ref + ",https://github.com/advisories/" + cve2githubID[cve] + "\n")

fout.close()
