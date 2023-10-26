import requests
import json


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
    print(f"\n{data}")

    author_name = data["search-results"]["entry"][0]["preferred-name"]["surname"]
    affiliation = data["search-results"]["entry"][0]["affiliation-current"]["affiliation-name"]
    document_count = data["search-results"]["opensearch:totalResults"]
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

    resp = requests.get(f"http://api.elsevier.com/content/author?author_id={author_id}&view=metrics",
                        headers={'Accept': 'application/json',
                                 'X-ELS-APIKey': "a689511f7a1e021667fba149228b2201"})

    print("\n")
    print(json.dumps(resp.json(),
               sort_keys=True,
               indent=4, separators=(',', ': ')))

    resp = requests.get(
        f"http://api.elsevier.com/content/search/scopus?query=AU-ID({author_id})&field=dc:identifier&count=100",
        headers={'Accept': 'application/json',
                 'X-ELS-APIKey': "a689511f7a1e021667fba149228b2201"})

    results = resp.json()

    print(f"\n{[[str(r['dc:identifier'])] for r in results['search-results']['entry']]}")


    def get_scopus_info(SCOPUS_ID):
        url = "http://api.elsevier.com/content/abstract/scopus_id/" + SCOPUS_ID +\
              "?field=authors,title,publicationName,volume,issueIdentifier" \
              ",prism:pageRange,coverDate,article-number,doi,citedby-count,prism:aggregationType"
        resp = requests.get(url,
                            headers={'Accept': 'application/json', 'X-ELS-APIKey': "a689511f7a1e021667fba149228b2201"})
        results = json.loads(resp.text.encode('utf-8'))

        fstring = '{authors}, {title}, {journal}, {volume}, {articlenum}, ({date}). {doi} (cited {cites} times).\n'
        return fstring.format(
            authors=', '.join(
                [au['ce:indexed-name'] for au in results['abstracts-retrieval-response']['authors']['author']]),
            title=results['abstracts-retrieval-response']['coredata'].get('dc:title', ''),
            journal=results['abstracts-retrieval-response']['coredata'].get('prism:publicationName', ''),
            volume=results['abstracts-retrieval-response']['coredata'].get('prism:volume', ''),
            articlenum=(results['abstracts-retrieval-response']['coredata'].get('prism:pageRange') or
                        results['abstracts-retrieval-response']['coredata'].get('article-number', '')),
            date=results['abstracts-retrieval-response']['coredata'].get('prism:coverDate', ''),
            doi='doi:' + results['abstracts-retrieval-response']['coredata'].get('prism:doi', ''),
            cites=int(results['abstracts-retrieval-response']['coredata'].get('citedby-count', 0))
        )


    doc_id=input("\nplease insert the document id: ")

    print(f"\n{get_scopus_info(doc_id)}")


    # orcid, surname, given/name, document count, subject area, what frequency means, affiliation name, city, and country


except requests.exceptions.RequestException as e:
    print(f"An error occurred during the request: {e}")
except (KeyError, IndexError):
    print("Unable to retrieve author information.")
except json.JSONDecodeError:
    print("Unable to parse the response data.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")