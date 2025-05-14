import json
import openai
from openai import OpenAI
import os


cve_list = set([])

package2cve = {}

home_dir = os.path.expanduser("~")
os.environ["OPENAI_API_KEY"] = json.load(open(home_dir + "/secret.json", "r"))["openai"]
openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])


def get_package_from_cve(cve_description):
    prompt = f"""
    Given the following CVE description, select the ecosystem that is affected.
    Only say one of the following: maven, npm, pip, go, c/c++, not know. If you are not sure, say not know.

    CVE Description:
    {cve_description}

    Affected package or library:
    """
    try:
        # Query OpenAI GPT model
        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages = [{"role": "user", "content": prompt}],
        )
        import pdb; pdb.set_trace()
        # Extract and return the identified package
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

for year in range(2002, 2025):
    print(year)
    if year != 2022: continue
    with open(f"../../NVD/nvdcve-1.1-{year}.json", "r") as fin:
        data = json.load(fin)
        for idx in range(len(data["CVE_Items"])):
            cve_id = data["CVE_Items"][idx]["cve"]["CVE_data_meta"]["ID"]
            if cve_id != "CVE-2022-31052": continue
            desc = data["CVE_Items"][idx]["cve"]["description"]["description_data"][0]["value"]
            package = get_package_from_cve(desc)
            import pdb; pdb.set_trace()
            cve_list.add(data["CVE_Items"][idx]["cve"]["CVE_data_meta"]["ID"])

cve_list = list(cve_list)

print(len(cve_list))
json.dump(cve_list, open("../../NVD/cve_list.json", "w"))
