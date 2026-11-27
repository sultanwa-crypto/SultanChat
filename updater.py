import json
import urllib.request

url = "https://api.github.com/repos/sultanwa-crypto/SultanChat/releases/latest"
response = urllib.request.urlopen(url)
data = response.read()
text = data.decode()
release = json.loads(text)

if open("version.txt").read().strip() != release["tag_name"]:
    print("update available!")

else:
    print("up to date.")