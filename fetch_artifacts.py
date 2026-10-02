import urllib.request, json, os, shutil, zipfile
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Remember the project root so we can always navigate back
PROJECT_ROOT = os.getcwd()


def extract_firmware(zip_url, hash_val):
    """Download and extract firmware.zip into the hash directory, idempotently."""
    urllib.request.urlretrieve(zip_url, 'firmware.zip')
    with zipfile.ZipFile('firmware.zip', 'r') as zip_ref:
        zip_ref.extractall('extracted_temp')

    for item in os.listdir('extracted_temp/firmware'):
        src = os.path.join('extracted_temp/firmware', item)
        dst = os.path.join(hash_val, item)
        # Remove existing destination to make re-runs idempotent
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        shutil.move(src, hash_val)

    shutil.rmtree('extracted_temp')
    os.remove('firmware.zip')


# ── Firmware ──────────────────────────────────────────────────────────────────
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
        extract_firmware(zip_url, hash_val)
    except Exception as e:
        print(f'Failed for {hash_val}: {e}')
        # Clean up partial state
        if os.path.exists('extracted_temp'):
            shutil.rmtree('extracted_temp')
        if os.path.exists('firmware.zip'):
            os.remove('firmware.zip')

master_hash = data['branches'].get('master')
if master_hash and os.path.exists(os.path.join(master_hash, 'hardware')):
    if os.path.exists('hardware'):
        shutil.rmtree('hardware')
    shutil.copytree(os.path.join(master_hash, 'hardware'), 'hardware')
elif not master_hash:
    print('Warning: master branch not found in index.json, skipping hardware copy')

print('Firmware artifacts fetched successfully!')


# ── Backpack ──────────────────────────────────────────────────────────────────
# Return to project root before navigating to backpack directory
os.chdir(PROJECT_ROOT)
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
            extract_firmware(zip_url, hash_val)
        except Exception as e:
            print(f'Backpack failed for {hash_val}: {e}')
            if os.path.exists('extracted_temp'):
                shutil.rmtree('extracted_temp')
            if os.path.exists('firmware.zip'):
                os.remove('firmware.zip')
    master_hash = data['branches']['master']
    if os.path.exists(os.path.join(master_hash, 'hardware')):
        if os.path.exists('hardware'):
            shutil.rmtree('hardware')
        shutil.copytree(os.path.join(master_hash, 'hardware'), 'hardware')
except Exception as e:
    print(f'Backpack fetch skipped: {e}')

print('Backpack artifacts fetched successfully!')
