import httpx
from selectolax.parser import HTMLParser


## Province Data
# 63 : "Western",
# 64 : "Central",
# 65 : "Southern",
# 66 : "Northern",
# 67 : "Eastern",
# 68 : "North-Western",
# 69 : "North-Central",
# 70 : "Uva",
# 71 : "Sabaragamuwa" 

def  get_district(province_id):
    url = "http://apps.moha.gov.lk:8090/lifecode/views/fetch.php"
    form_data = {"action": "province", "query": province_id}
    
    res = httpx.post(url, data=form_data).json()
    
    # Get the HTML string from the response JSON object.
    parser = HTMLParser(res.get('output'))
    
    # Extract the option tags
    option_tags = parser.css("option")
    
    district_dict = {}

    for option in option_tags:
        if option.attributes.get("value") is not None:
            value = option.attributes.get("value")
            text = option.text()
            district_dict[value] = text
    
    return district_dict


def main():
    districts = get_district(66)
    for key in districts.keys():
        print (key)

    # Get the list of GN as a HTML table
    target_url = "http://apps.moha.gov.lk:8090/lifecode/views/rpt_gn_list.php"
    r = httpx.post(target_url, data={"district": "55", "province":"66"})
    r.text


    # Parse the HTML, access the body and 
    # create CSV with header <th> title.
    # Loop through each row.
        # append each row in to CSV
    
    # export CSV

if __name__ == "__main__":
    main()