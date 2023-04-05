import httpx
from selectolax.parser import HTMLParser
import pandas as pd

province_dict = {
    63: "Western",
    64: "Central",
    65: "Southern",
    66: "Northern",
    67: "Eastern",
    68: "North-Western",
    69: "North-Central",
    70: "Uva",
    71: "Sabaragamuwa"
}


def get_district(province_id: int):
    url = "http://apps.moha.gov.lk:8090/lifecode/views/fetch.php"
    form_data = {"action": "province", "query": province_id}

    res = httpx.post(url, data=form_data).json()

    # Get the HTML string from the response -> JSON object.
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


def clean_and_fix_data(df: pd.DataFrame):

    # Clean data
    df['Province'] = df['Province'].apply(lambda x: x.split(':')[-1].strip())
    df['District'] = df['District'].apply(lambda x: x.split(':')[-1].strip())
    df['Divisional Secretariat'] = df['Divisional Secretariat'].apply(
        lambda x: x.split(':')[-1].strip())

    # Split LIFe Code into multiple columns to by delemeter
    df[["province_code", "district_code", "division_code", "gnd_code (new)"]
       ] = df["LIFe Code"].str.split("-", expand=True)
    df[["province_si", "province_ta", "province_en"]
       ] = df["Province"].str.split("/ ", expand=True)
    df[["district_si", "district_ta", "district_en"]
       ] = df["District"].str.split("/ ", expand=True)
    df[["division_si", "division_ta", "division_en"]
       ] = df["Divisional Secretariat"].str.split("/ ", expand=True)

    # Delete unwanted columns
    df = df.drop(
        ['Province', 'District', 'Divisional Secretariat', 'GN Code'], axis=1)

    # Rename columns
    df = df.rename(columns={
        'Name in Sinhala': 'gn_si',
        'Name in Tamil': 'gn_ta',
        'Name in English': 'gn_en',
        'MPA Code': 'gnd_code (old)',
        'LIFe Code': 'location_code_of_gnd'
    })

    df = df.reindex(columns=[
        'location_code_of_gnd',
        'gnd_code (new)',
        'gn_en',
        'gn_ta',
        'gn_si',
        'gnd_code (old)',
        'division_code',
        'division_en',
        'division_ta',
        'division_si',
        'district_code',
        'district_en',
        'district_ta',
        'district_si',
        'province_code',
        'province_en',
        'province_ta',
        'province_si',
    ])

    return df


def main():

    rows = []
    headings = []
    for p_key in province_dict.keys():
        districts = get_district(p_key)
        for d_key in districts.keys():
            # Get the list of GN as a HTML table
            target_url = "http://apps.moha.gov.lk:8090/lifecode/views/rpt_gn_list.php"
            res = httpx.post(target_url, data={
                "district": f"{d_key}", "province": f"{p_key}"})

            # Parse the HTML, access the body and
            parser = HTMLParser(res.text)

            # Extract the text content from each heading element
            th_element = parser.css("th")
            headings = [th.text() for th in parser.css("table th")]

            # Extract all rows from the table
            for tr in parser.css("table tbody tr"):
                row = []
                for td in tr.css("td"):
                    row.append(td.text().replace('\u200b', '').replace(
                        '\u200E', '').replace('‍', ''))
                rows.append(row)

    # Create a dataFrame & export as Excel
    df = pd.DataFrame(rows, columns=headings)
    df.to_excel('source_gn_data.xlsx', index=False)

    # After pre-process
    clean_and_fix_data(df).to_excel('cleanned_gn_list.xlsx', index=False)


if __name__ == "__main__":
    main()
