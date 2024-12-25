from flask import Flask, request, jsonify

app = Flask(__name__)

def weather_data(where: str = None, when: str = None) -> str:
    '''
    given a location and a time period, this custom function
    returns weather forecast description in natural language.

    This is a mockup function, returning a fixed text tempalte.
    The function could wrap an external API returning realtime weather forecast.

    parameters:
        where: location as text, e.g. 'Genova, Italy'
        when: time period, e.g. 'today, now'

    returns:
        weather forecast description as flat text.
    '''
    if where and when:
        # return a fake/hardcoded weather forecast sentence
        return f'in {where}, {when} is sunny! Temperature is 20 degrees Celsius.'
    elif not where:
        return 'where?'
    elif not when:
        return 'when?'
    else:
        return 'I don\'t know'

def weather(action_input: dict) -> str:
    where = action_input["location"]
    when = action_input["date"]
    return weather_data(where=where, when=when)

@app.route('/process', methods=['POST'])
def process_request():
    try:
        data = request.get_json()  # Get JSON payload from the request
        print(data)

        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400

        result = {}
        result["output"] = weather(data["payload"])

        return jsonify(result)  # Sending back the JSON payload as response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50001, debug=True)
