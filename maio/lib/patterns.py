import re
import string

UUID_RE = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
OBJECT_ID_RE = "[0-9a-fA-F]{24}"
TAG_RE = re.compile(r'(<!--.*?-->|<[^>]*>)')
CHARACTERS = string.ascii_letters + string.digits
EMAIL_RE = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
JUST_NAME_RE = '\w+'
