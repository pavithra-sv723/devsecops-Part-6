from bs4 import BeautifulSoup

def parse_zap_report(file_path):
    with open(file_path, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Find the table containing vulnerabilities
    vulnerabilities = []
    for table in soup.find_all('table'):
        # Assuming the first row is the header
        headers = [th.text.strip() for th in table.find_all('th')]
        if 'Risk Level' in headers:
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                columns = row.find_all('td')
                risk_level = columns[headers.index('Risk Level')].text.strip()
                if 'Medium' in risk_level:
                    vulnerabilities.append({
                        'name': columns[headers.index('Name')].text.strip(),
                        'description': columns[headers.index('Description')].text.strip()
                    })
    return vulnerabilities

# Parse the ZAP report
vulnerabilities = parse_zap_report('zap-report.html')
if vulnerabilities:
    print(f"Found {len(vulnerabilities)} Medium vulnerabilities:")
    for vuln in vulnerabilities:
        print(f"- {vuln['name']}: {vuln['description']}")
else:
    print("No Medium vulnerabilities found.")
