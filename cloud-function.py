"""
- In the first instance we wont check the uniqueness each company name, we will need to manage this ourselves as admins via the PRs
- Repo will "Require pull request reviews before merging"
- Example Ref to payload: https://github.com/dhughesni/example-cloud-hooks/settings/hooks/187994855
- Need to ensure the correct service account is set for cloud fucntion - it should be tech-control...
"""
import json
from google.cloud import firestore
import requests

db = firestore.Client()

def check_master_branch(payload):
    return True if payload['ref'] == "refs/heads/master" else False

def get_data_from_github(file):
    print('get_data_from_github', file)
    r = requests.get('https://raw.githubusercontent.com/dhughesni/example-cloud-hooks/master/'+file)
    return json.loads(r.content)

def process(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    if check_master_branch(request_json):
        try:
            # TODO: verify that the file is json, this needs to be done for removed,added,modified as there may be edge cases we need to handle
            # DONE: removed .json from company_id
            for i in request_json["head_commit"]["removed"]: # delete data
                print('deleting', i)
                company_id = i.replace('companies/', '').replace('.json', '')
                db.collection("locations").document("belfast").collection("companies").document(company_id).delete()
            for i in request_json["head_commit"]["added"]: # add data
                print('adding', i)
                company_id = i.replace('companies/', '').replace('.json', '')
                company_data = get_data_from_github(i)
                db.collection("locations").document("belfast").collection("companies").add(company_data, company_id)
            for i in request_json["head_commit"]["modified"]: # edit - update data
                print('updating', i)
                company_id = i.replace('companies/', '').replace('.json', '')
                company_data = get_data_from_github(i)
                db.collection("locations").document("belfast").collection("companies").document(company_id).update(company_data)
        except Exception as err:
            print("Process Function Exception:", err)
    else: # return None if nothing to do
        print("Nothing to be done for this branch")