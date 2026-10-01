import urllib.request, json, os, shutil
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

os.makedirs('public/assets/firmware', exist_ok=True)
os.chdir('public/assets/firmware')

req = urllib.request.Request('https://poisedundead.github.io/Custom-ExpressLRS/ExpressLRS/index.json', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as url:
    data = json.loads(url.read().decode())

with open('index.json', 'w') as f:
    json.dump(data, f)

for hash_val in set(list(data['tags'].values()) + list(data['branches'].values())):
    if not os.path.exists(hash_val):
        os.makedirs(hash_val)
    zip_url = f'https://poisedundead.github.io/Custom-ExpressLRS/ExpressLRS/{hash_val}/firmware.zip'
    try:
        urllib.request.urlretrieve(zip_url, 'firmware.zip')
        os.system('unzip -q firmware.zip -d extracted_temp')
        
        for item in os.listdir('extracted_temp/firmware'):
            shutil.move(os.path.join('extracted_temp/firmware', item), hash_val)
            
        shutil.rmtree('extracted_temp')
        os.remove('firmware.zip')
    except Exception as e:
        print(f'Failed for {hash_val}: {e}')

master_hash = data['branches']['master']
if os.path.exists(os.path.join(master_hash, 'hardware')):
    if os.path.exists('hardware'):
        shutil.rmtree('hardware')
    shutil.copytree(os.path.join(master_hash, 'hardware'), 'hardware')

print('Firmware artifacts fetched successfully!')


os.chdir('../../')
os.makedirs('public/assets/backpack', exist_ok=True)
os.chdir('public/assets/backpack')

req = urllib.request.Request('https://artifactory.expresslrs.org/Backpack/index.json', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as url:
        data = json.loads(url.read().decode())
    with open('index.json', 'w') as f:
        json.dump(data, f)
    for hash_val in set(list(data['tags'].values()) + list(data['branches'].values())):
        if not os.path.exists(hash_val):
            os.makedirs(hash_val)
        zip_url = f'https://artifactory.expresslrs.org/Backpack/{hash_val}/firmware.zip'
        try:
            urllib.request.urlretrieve(zip_url, 'firmware.zip')
            os.system('unzip -q firmware.zip -d extracted_temp')
            for item in os.listdir('extracted_temp/firmware'):
                shutil.move(os.path.join('extracted_temp/firmware', item), hash_val)
            shutil.rmtree('extracted_temp')
            os.remove('firmware.zip')
        except:
            pass
    master_hash = data['branches']['master']
    if os.path.exists(os.path.join(master_hash, 'hardware')):
        if os.path.exists('hardware'):
            shutil.rmtree('hardware')
        shutil.copytree(os.path.join(master_hash, 'hardware'), 'hardware')
except:
    pass

print('Backpack artifacts fetched successfully!')

