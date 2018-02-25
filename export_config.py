import sys
import requests
from xml.etree import ElementTree

gsa_admin_url = "http://gsa.host:8000"

admin_username = "admin"
admin_password = "password"

config_file_path = "config.xml"
config_file_password = "12345678"  #  8 chars minimum


def main(argv):
    login_url = gsa_admin_url + "/accounts/ClientLogin?Email=" + admin_username + "&Passwd=" + admin_password
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    print("Requesting auth token...")

    r1 = requests.post(login_url, headers=headers)

    if r1.status_code != 200:
        print("ERROR: Request returned status " + str(r1.status_code))
        print('"' + r1.text + '"')
        print("> Check that the admin username and password are correct")
        return

    token = r1.text[r1.text.index("Auth=") + 5:].strip()

    export_url = gsa_admin_url + "/feeds/config/importExport?password=" + config_file_password
    headers = {"Content-type": "application/atom+xml", "Authorization": "GoogleLogin auth=" + token}

    print("Exporting GSA configuration...")

    r2 = requests.get(export_url, headers=headers)

    if r2.status_code != 200:
        print("ERROR: Request returned status " + str(r2.status_code) + ":")
        print('"' + r2.text + '"')
        print("> Check that the configuration password is at least 8 characters long")
        return

    root = ElementTree.fromstring(r2.text)

    if root.tag == "{http://schemas.google.com/g/2005}errors":
        print("ERROR: " + root.find("{http://schemas.google.com/g/2005}error").find(
            "{http://schemas.google.com/g/2005}internalReason").text)
        return

    content_tags = root.findall("{http://schemas.google.com/gsa/2007}content")

    if len(content_tags) < 2:
        print("ERROR: Bad response")
        return

    config = content_tags[1].text

    print("Writing config to '" + config_file_path + "'...")

    with open(config_file_path, "w") as output_file:
        output_file.write(config)

    print("Done")


if __name__ == '__main__':
    main(sys.argv)
