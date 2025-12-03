import re
import sys

PATTERNS = [
    (r'PAYMENT_TOKEN\s*=\s*"', 'Hardcoded PAYMENT_TOKEN'),
    (r'MAIL_SERVER_KEY\s*=\s*"', 'Hardcoded MAIL_SERVER_KEY'),
    (r'INTERNAL_AUTH\s*=\s*"', 'Hardcoded INTERNAL_AUTH'),
    (r"hashlib\.md5\(", 'Use of insecure MD5 hashing'),
    (r"%\s*\",\s*\w+\s*\%", 'String formatting into SQL (possible SQLi)') ,
    (r"SELECT .*%s", 'SQL string formatting found'),
    (r"subprocess\.Popen\(.*shell=\s*True", 'subprocess with shell=True (command injection)'),
    (r"app\.run\(debug=\s*True\)", 'Running Flask in debug mode'),
]


def scan_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    findings = []
    for pat, desc in PATTERNS:
        if re.search(pat, txt):
            findings.append(desc)
    # Additional heuristic
    if 'notify_url' in txt and 'https' not in txt:
        findings.append('Potential non-HTTPS notify_url usage')
    return findings


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: test_inputs.py <file>')
        sys.exit(2)
    path = sys.argv[1]
    findings = scan_file(path)
    if findings:
        print('INSECURE:', path)
        for f in findings:
            print(' -', f)
        sys.exit(1)
    else:
        print('OK:', path)
        sys.exit(0)
