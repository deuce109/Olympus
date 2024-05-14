import re

github_api_re = re.compile(r"https:\/\/api\.github\.com\/repos\/([a-zA-Z0-9:\?#[\]@!$&'()*+,;%=-]+\/[a-zA-Z0-9:\?#[\]@!$&'()*+,;%=-]+)\/releases")

github_ui_repo_re = re.compile(r"https:\/\/github\.com\/([a-zA-Z0-9:\?#[\]@!$&'()*+,;%=-]+\/[a-zA-Z0-9:\?#[\]@!$&'()*+,;%=-]+)\/releases")