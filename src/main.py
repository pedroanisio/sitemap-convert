# File: xml_to_json_converter.py
# Path: /path/to/project/app/services/xml_to_json_converter.py
# Author: [Your Name]
# Purpose: Microservice to convert XML content from sitemaps to JSON format using untangle.
# Modification History:
# - [Date] - [Your Name] - [Changes made]

from flask import Flask, request, jsonify
import requests
import untangle
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def convert_xml_to_json(xml_content: str) -> dict:
    """
    Converts XML content to a JSON-friendly dictionary format using the untangle library.

    Args:
        xml_content (str): String representation of XML content.

    Returns:
        dict: A dictionary representation of the XML content, more suitable for JSON conversion.
    """
    try:
        obj = untangle.parse(xml_content)
        result = {
            "urlset": [{
                "loc": url.loc.cdata,
                "lastmod": url.lastmod.cdata,
                "changefreq": url.changefreq.cdata
            } for url in obj.urlset.url]
        }
        return result
    except Exception as e:  # Catching general exceptions for robust error handling
        logging.error("Failed to parse XML content: {}".format(e))
        raise ValueError("Invalid XML content.") from e

@app.route('/convert', methods=['POST'])
def convert():
    """
    API endpoint to convert XML from sitemap URLs to JSON.

    Expects a JSON payload with a 'sitemaps' key containing a list of URLs.
    """
    data = request.get_json()
    if not data or 'sitemaps' not in data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    results = []
    for url in data['sitemaps']:
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = convert_xml_to_json(response.text)
            results.append({"url": url, "data": json_data})
        except requests.RequestException:
            results.append({"url": url, "error": "Failed to retrieve the sitemap"})
        except ValueError as e:
            results.append({"url": url, "error": str(e)})

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
