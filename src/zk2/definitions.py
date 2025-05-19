AUTHOR = "author"
DATE = "date"
ID = "id"
MODIFIED = "modified"
TAGS = "tags"
TITLE = "title"
ARCHIVED = "archived"

HEADER_KEYS = [DATE, MODIFIED, ID, AUTHOR, TAGS, TITLE]

BODY = "body"
ALL_KEYS = HEADER_KEYS + [BODY]


HEADER_LINE_REGEX = r"^([a-zA-Z][a-zA-Z0-9_]*):\s*(.*)\s*"
ANFANG_REGEX = r"^((?:\S+\s+){1,6})"
ZK_LINK_REGEX = r"zk://[0-9]{12,}"
ZK_QUERY_REGEX = r'([^"@]+)*("[^@]+)?(@\d+)?'
