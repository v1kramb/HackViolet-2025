import requests
import json

RELEVANCE_THRESHOLD = 75
BILL_RATE_LIMIT = 10

def get_req(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def state_abbreviation_to_name(abbreviation):
    states = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }
    return states.get(abbreviation.upper(), "Unknown abbreviation")

f = open('sample_bill_file.txt', 'w')

search_query = 'https://api.legiscan.com/?key=ea9e31e3ebdf68bef6a2af7d15247f3b&op=getSearchRaw&query=abortion+OR+pregnancy'
search = get_req(search_query)

bill_ids = set()

count = 0  # rate limits
for result in search['searchresult']['results']:
    if result['relevance'] < RELEVANCE_THRESHOLD or count > BILL_RATE_LIMIT:
        break
    bill_id = result['bill_id']

    if bill_id in bill_ids:
        continue

    bill_ids.add(bill_id)
    bill_query = f"https://api.legiscan.com/?key=ea9e31e3ebdf68bef6a2af7d15247f3b&op=getBill&id={bill_id}"
    bill = get_req(bill_query)

    if bill['status'] == 'OK':
        state_name = state_abbreviation_to_name(bill['bill']['state'])
        bill_number = bill['bill']['bill_number']
        bill_year = bill['bill']['session']['year_end']
        bill_desc = bill['bill']['description']
        s = f"In {bill_year}, {state_name} passed {bill_number}.\nDescription: {bill_desc}\n\n"
        f.write(s)

    count += 1