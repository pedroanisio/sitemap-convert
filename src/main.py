import requests
import untangle
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

class SitemapConverter:
    def __init__(self):
        pass

    def convert_to_json(self, xml_data: str) -> dict:
        """
        Converts XML data to a JSON-like dictionary using untangle.

        Args:
            xml_data (str): XML content as a string.

        Returns:
            dict: JSON-like dictionary representing the XML structure.
        """
        try:
            obj = untangle.parse(xml_data)
            return self._to_dict(obj)
        except Exception as e:
            logging.error(f"Error converting XML to JSON: {e}")
            raise ValueError("Failed to parse XML.")

    def _to_dict(self, obj):
        """
        Recursively converts an untangle object into a dictionary, handling namespaces and attributes.

        Args:
            obj: An untangle object.

        Returns:
            dict or list: A dictionary representation of the untangle object, or a list if multiple children.
        """
        if not hasattr(obj, 'children') or not obj.children:
            return obj.cdata.strip() if obj.cdata else None
        if len(obj.children) == 1 and not isinstance(obj.children[0], untangle.Element):
            return obj.children[0].cdata.strip()
        result = {}
        for child in obj.children:
            child_name = child._name.split(':')[-1]  # Strip namespace if any
            child_value = self._to_dict(child)
            if child_name in result:
                if not isinstance(result[child_name], list):
                    result[child_name] = [result[child_name]]
                result[child_name].append(child_value)
            else:
                result[child_name] = child_value
        return result

@app.route('/convert', methods=['POST'])
def convert():
    """
    API endpoint to receive a list of XML sitemap URLs and convert them to JSON.

    Expects a JSON payload with 'sitemaps' key containing a list of URLs.
    """
    data = request.get_json()
    if not data or 'sitemaps' not in data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    converter = SitemapConverter()
    results = None

    for url in data['sitemaps']:
        try:
            response = requests.get(url)
            response.raise_for_status()  # ensures we raise an exception for bad responses
            json_data = converter.convert_to_json(response.text)
            results = {"url": url, "data": json_data}
        except requests.RequestException as e:
            results = {"url": url, "error": "Failed to retrieve the sitemap: " + str(e)}
        except ValueError as e:
            results = {"url": url, "error": "Conversion error: " + str(e)}

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
