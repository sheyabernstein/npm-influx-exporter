import re

HTTP_METHOD_PATTERN = re.compile(r"GET|POST|PUT|DELETE|PATCH")
HTTP_STATUS_PATTERN = re.compile(r"\] (- )?(?P<status>\d{3}) ")
HTTP_PATH_PATTERN = re.compile(r"(?=\")[\S]+(?<=\")")

TIMESTAMP_PATTERN = re.compile(r"\d+/\S+/\d{4}:\d{2}:\d{2}:\d{2} \+\d{4}")

LENGTH_PATTERN = re.compile(r"(?<=\[Length )\d+(?=\])")

IP_PATTERN = re.compile(r"(([0-9]{1,3}[\.]){3}[0-9]{1,3})")

TARGET_DOMAIN_PATTERN = re.compile(r" (?P<domain>[\S\.]+) \"")
