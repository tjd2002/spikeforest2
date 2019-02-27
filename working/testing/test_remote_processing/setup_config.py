import json
from cairio import client as ca
import os
os.environ['KBUCKET_URL'] = 'http://localhost:63240'

upload_token = 'test_upload_token'
cairio_url = 'http://localhost:10001'
collection_name = 'collection1'
collection_token = 'token1'
admin_token = 'test_admin_token'
share_id = '946631a0304e'
password = 'test_password'

ca.setRemoteConfig(url=cairio_url)

ca.addRemoteCollection(
    collection=collection_name,
    token=collection_token,
    admin_token=admin_token
)

config = dict(
    url=cairio_url,
    collection=collection_name,
    token=collection_token,
    share_id=share_id,
    upload_token=upload_token
)

ca.setRemoteConfig(**config)

ca.setValue(key='test-readwrite', value=json.dumps(config), password=password)

config = dict(
    url=cairio_url,
    collection=collection_name,
    token=collection_token,
    share_id=share_id,
    upload_token=upload_token
)

ca.setRemoteConfig(url='https://pairio.org:20443')
ca.addRemoteCollection(collection='test_collection1',token='test_token1',admin_token=os.environ['CAIRIO_ADMIN_TOKEN'])

config = dict(
    url='https://pairio.org:20443',
    collection='test_collection1',
    token='test_token1',
    share_id=share_id,
    upload_token=upload_token
)

ca.setRemoteConfig(**config)
ca.setValue(key='test-readwrite-remote-cairio', value=json.dumps(config), password=password)