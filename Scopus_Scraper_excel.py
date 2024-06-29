import requests
import json
import pandas as pd


# Function to retrieve detailed information about a document from Scopus
def get_scopus_info(SCOPUS_ID):
    url = "http://api.elsevier.com/content/abstract/scopus_id/" + SCOPUS_ID + \
          "?field=authors,title,publicationName,volume,issueIdentifier" \
          ",prism:pageRange,coverDate,article-number,doi,citedby-count,prism:aggregationType"
    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': 'a689511f7a1e021667fba149228b2201'
    }
    resp = requests.get(url, headers=headers)
    results = resp.json()

    if 'abstracts-retrieval-response' in results and 'authors' in results['abstracts-retrieval-response']:
        authors = ', '.join(
            [au.get('ce:indexed-name', '') for au in results['abstracts-retrieval-response']['authors']['author']])
    else:
        authors = ''

    return {
        'Authors': authors,
        'Title': results['abstracts-retrieval-response']['coredata'].get('dc:title', ''),
        'Journal': results['abstracts-retrieval-response']['coredata'].get('prism:publicationName', ''),
        'Volume': results['abstracts-retrieval-response']['coredata'].get('prism:volume', ''),
        'Pages': results['abstracts-retrieval-response']['coredata'].get('prism:pageRange', '') or
                 results['abstracts-retrieval-response']['coredata'].get('article-number', ''),
        'Date': results['abstracts-retrieval-response']['coredata'].get('prism:coverDate', ''),
        'DOI': results['abstracts-retrieval-response']['coredata'].get('prism:doi', ''),
        'Cited By': int(results['abstracts-retrieval-response']['coredata'].get('citedby-count', 0))
    }


try:
    author_id = input("Enter Author ID: ")

    url = f"https://api.elsevier.com/content/search/author?query=AU-ID({author_id})"
    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": "a689511f7a1e021667fba149228b2201"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = json.loads(response.text)
    author_name = data["search-results"]["entry"][0]["preferred-name"]["surname"]
    affiliation = data["search-results"]["entry"][0]["affiliation-current"]["affiliation-name"]

    # Retrieve document count
    document_count = data["search-results"]["opensearch:totalResults"]

    # Retrieve additional author details
    affiliation_info = data["search-results"]["entry"][0].get("affiliation-current", {})
    city = affiliation_info.get("affiliation-city")
    country = affiliation_info.get("affiliation-country")
    orcid = data["search-results"]["entry"][0].get("orcid")
    subject_areas = data["search-results"]["entry"][0].get("subject-area", [])

    print(f"\nAuthor name: {author_name}")
    print(f"Affiliation: {affiliation}")
    print(f"Document count: {document_count}")

    # Print city, country, and subject area if available
    if city:
        print(f"City: {city}")
    if country:
        print(f"Country: {country}")
    if orcid:
        print(f"ORCID: {orcid}")
    if subject_areas:
        print("Subject areas:")
        for area in subject_areas:
            subject_area = area["$"]
            subject_area_abbrev = area["@abbrev"]
            frequency = area["@frequency"]
            print(f"{subject_area_abbrev} - {subject_area} (Frequency: {frequency})")

    # Retrieve documents from Scopus
    resp = requests.get(
        f"http://api.elsevier.com/content/search/scopus?query=AU-ID({author_id})&field=dc:identifier&count=100",
        headers={'Accept': 'application/json', 'X-ELS-APIKey': "a689511f7a1e021667fba149228b2201"})

    results = resp.json()

    documents = []
    for r in results['search-results']['entry']:
        scopus_id = r['dc:identifier']
        document_info = get_scopus_info(scopus_id)
        documents.append(document_info)

    # Create dataframe
    df = pd.DataFrame(documents, columns=['Authors', 'Title', 'Journal', 'Volume', 'Pages', 'Date', 'DOI', 'Cited By'])

    # Write dataframe to Excel
    excel_filename = f"{author_name}_documents.xlsx"
    df.to_excel(excel_filename, index=False)
    print(f"\nExcel file '{excel_filename}' successfully created with document details.")

except requests.exceptions.RequestException as e:
    print(f"An error occurred during the request: {e}")
except (KeyError, IndexError):
    print("Unable to retrieve author information.")
except json.JSONDecodeError:
    print("Unable to parse the response data.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")