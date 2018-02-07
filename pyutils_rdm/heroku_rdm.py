import os
import json
import requests
from pyutils_rdm import dir_to_tarfile, look_in_tar, push_to_github

github_account = os.environ.get('GITHUB_USERNAME', None)
github_password = os.environ.get('GITHUB_PASSWORD', None)

tar_app_name = 'tar-app-source-rdm'
heroku_url = 'https://api.heroku.com/'
heroku_build_path = heroku_url + 'apps/{}/{}'
heroku_setup_path = heroku_url + 'app-setups'
github_url = "https://api.github.com/repos/{}/{}/tarball/master" 
headers = {'content-type': 'application/json',
           'Accept': 'application/vnd.heroku+json; version=3',
           'Authorization': 'Bearer ' + os.environ.get('HEROKU_AUTH', None)}

result_url = 'https://api.heroku.com/apps/start-rdm/builds/d370f8f1-43e5-4f1d-ba23-aec01b64de49/result'
#r = requests.get(result_url, headers=headers)

def upload_tar(heroku_app_name,tarfile='temp.tar'):
    r = requests.post(heroku_build_path.format(heroku_app_name, 'sources'), headers=headers)
    if 'source_blob' not in r.json():
        print(r.json())
    get_url = r.json()['source_blob']['get_url']
    with open(tarfile, 'rb') as fh:
        filedata = fh.read()
    file_headers = headers.copy()
    file_headers['content-type'] = 'application/octet-stream'
    r = requests.put(r.json()['source_blob']['put_url'], data=filedata)
    #os.system('rm newfile.tar')
    #os.system("wget -O newfile.tar '{}'".format(get_url))
    #look_in_tar('newfile.tar')
    return get_url

def push_to_heroku(tar_url,heroku_app_name, build_type):
    data = { "source_blob": { "url": tar_url } }
    if build_type == 'setup':
        heroku_path = heroku_setup_path
    else:
        heroku_path = heroku_build_path.format(heroku_app_name, 'builds')
    r = requests.post(heroku_path, data=json.dumps(data), headers=headers)
    return { 'push_id': r.json()['id'], 'app_name': heroku_app_name, 'build_type': build_type }

def push_from_github_to_heroku(build_type, repo_name,heroku_app_name,github_account=github_account):
    url = github_url.format(github_account, repo_name)
    return push_to_heroku(url, heroku_app_name, build_type)

def push_from_local_to_heroku(local_dir,heroku_app_name, build_type):
    global tar_app_name
    dir_to_tarfile(local_dir, ignore='.git')
    tar_url = upload_tar(heroku_app_name if build_type == 'build' else tar_app_name)
    return push_to_heroku(tar_url, heroku_app_name, build_type)

def push_from_site_to_heroku(*args):
    local_dir, heroku_app_name = args[:2]
    if heroku_app_name in list_apps()['app']:
        build_type = 'build'
    else:
        #There is no existing app to upload a tar file to.
        build_type = 'setup'
    from_github = False # pass github tarball url directly to heroku
    if 'github' in args and from_github:
        return push_from_github_to_heroku(build_type, *args[:-1])
    if build_type == 'build':
        return push_from_local_to_heroku(*args[:2], build_type)
    else:
        push_to_github(args[0], 'build-repo', 'No commit message.', github_account, github_password)
        return push_from_github_to_heroku(build_type, 'build-repo', heroku_app_name, github_account)
        

def list_apps():
    app_list = requests.get(heroku_url + 'apps', headers=headers).json()
    return { 'app': [i['name'] for i in app_list] }

def delete_app(app_name):
    response = requests.delete(
             heroku_url + 'apps/' + app_name,
             headers=headers).json()
    return { 'deleted_app': {k: response[k] for k in ('name', 'web_url')}}

def create_addon(app_name,addon,plan):
    return {
        'addon_name': requests.post(
             heroku_url + 'apps/' + app_name + '/addons/',
             data=json.dumps({
                 'attachment': {
                     'name': addon.upper(),
                 },
                 'plan': '{}:{}'.format(addon, plan)
             }),
             headers=headers).json()['plan']['name'],
         'on_app': app_name }

def create_app(app_name):
    response = requests.post(
             heroku_url + 'apps',
             data=json.dumps({'name': app_name}),
             headers=headers).json()
    items = ['name', 'web_url']
    if 'name' in response and 'web_url' in response:
        return { 'created_app': {k: response[k] for k in items}}
    else:
        return response

def add_papertrail(app_name):
    result = { 'addons': [] }
    result['addons'].append(create_addon(app_name, 'papertrail', 'choklad'))
    return result
    
def rename_app(old_name, new_name):
    response = requests.patch(
             heroku_url + 'apps/' + old_name,
             data=json.dumps({'name': new_name}),
             headers=headers).json()
    if 'name' in response and response['name'] == new_name:
        return { 'renamed_app': {
                     'old_name': old_name,
                     'new_name': response['name']
               }}
    else:
        return response