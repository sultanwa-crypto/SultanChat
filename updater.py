import json
import urllib.request
import zipfile

url = "https://api.github.com/repos/sultanwa-crypto/SultanChat/releases/latest"
response = urllib.request.urlopen(url)
data = response.read()
text = data.decode()
release = json.loads(text)

    print("update available!")
zip_url = release["zipball_url"]
zip_code = urllib.request.urlopen(zip_url)
zip_data = zip_code.read()
zip_file = open("update.zip", "wb")
zip_file.write(zip_data)
zip_file.close()
new_code = zipfile.ZipFile("update.zip", "r")
print(new_code.namelist())
