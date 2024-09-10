from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

app = Flask(__name__)

# Configure the API key
genai.configure(api_key='AIzaSyAoWw0u5oWMCC-zUfp1hg_pbhUG3SV1G3g')

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

# Set up the model
model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
verify_url = 'http://127.0.0.1:6666/auth/verify'

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():


    data = request.json
    headers = request.headers

    subject = data.get('subject', None)
    duration = data.get('num_days', None)
    year_of_study = data.get('year_of_study', None)
    country = data.get('country', None)

    email = headers.get('email', None)
    token = headers.get('token', None)

    if email is None or token is None:
        return jsonify({"error": "Provide TOKEN and EMAIL"}), 401
    data = {
        "token": token,
        "email": email
    }
    response = requests.post(verify_url, json=data)
    if response.status_code == 200:
        if response.text == "false`":
            return jsonify({"error": "Unauthorized"})
    else:
        print(f"Error: {response.status_code}, {response.text}")

    if subject is None or isinstance(subject, str) is False:
        return jsonify({"error": "No subject provided"}), 400
    elif duration is None or isinstance(duration, int) is False:
        return jsonify({"error": "No duration provided"}), 400
    elif year_of_study is None or isinstance(year_of_study, int) is False:
        return jsonify({"error": "No year of study provided"}), 400
    elif country is None or isinstance(country, str) is False:
        return jsonify({"error": "No country provided"}), 400

    prompt = prompt = f"""Generate a study plan overview based on the following input:

{{
  "subject": "{subject}",
  "num_lectures": {duration},
  "year_of_study": {year_of_study},
  "country": "{country}"
}}

Input field explanations:
- subject: The main area of study. This determines the overall focus of the study plan.
- num_lectures: The number of study sessions or "lectures" to plan for. This dictates how many days the study plan should cover.
- year_of_study: The year level of the student (e.g., 2 means second year of high school). This helps in determining the appropriate difficulty and depth of the topics.
- country: The country where the student is studying. This may influence the content based on specific educational standards or typical curriculum structures in that country.

Please provide the output in the following JSON format:

{{
  "plan_overview": [
    {{
      "day": 1,
      "topic": "string",
      "brief_description": "string (max 50 words)",
      "estimated_duration": "string (e.g., '2 hours')",
      "difficulty_level": "string (e.g., 'Intermediate')"
    }},
    // ... repeat for each day up to num_lectures
  ],
  "learning_objectives": [
    "string",
    // ... list 3-5 overall learning objectives
  ],
  "additional_resources": [
    {{
      "type": "string (e.g., 'Book')",
      "name": "string",
    }},
    // ... list 2-3 additional resources
  ]
}}

Output field explanations:
- plan_overview: An array of objects, each representing a day's study plan.
  - day: The sequential number of the study session.
  - topic: The main subject or concept to be studied that day.
  - brief_description: A concise explanation of what will be covered, limited to 50 words.
  - estimated_duration: The expected time needed for the study session.
  - difficulty_level: An indication of how challenging the material is expected to be.

- learning_objectives: An array of strings, each describing a key goal or skill the student should achieve by the end of the study plan.

- additional_resources: An array of objects providing extra materials for further study.
  - type: The category of the resource (e.g., book).
  - name: The title or name of the resource.

Ensure that the plan:
1. Is tailored to the specified year of study and country.
2. Covers fundamental Computer Science topics appropriate for specified student.
3. Progresses logically, building on previous topics.
4. Includes a mix of theoretical concepts and practical applications.
5. Takes into account any specific educational standards or focus areas common in the country provided.

The brief description for each day should give a clear idea of what will be covered, without going into extensive detail. Aim to provide a coherent and well-structured overview that a student can easily understand and follow.
"""

    try:
        response = model.generate_content(prompt)
        return jsonify(response.text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/day_details', methods=['POST'])
def day_details():
    data = request.json
    headers = request.headers

    day = data.get('day', None)
    subject = data.get('subject', None)
    year_of_study = data.get('year_of_study', None)
    country = data.get('country', None)
    dificulty_level = data.get('dificulty_level', None)
    topic = data.get('topic', None)

    email = headers.get('email', None)
    token = headers.get('token', None)

    if email is None or token is None:
        return jsonify({"error": "Provide TOKEN and EMAIL"}), 401
    data = {
        "token": token,
        "email": email
    }
    response = requests.post(verify_url, json=data)
    if response.status_code == 200:
        if response.text == "false`":
            return jsonify({"error": "Unauthorized"})
    else:
        print(f"Error: {response.status_code}, {response.text}")

    if day is None or isinstance(day, int) is False:
        return jsonify({"error": "No day specified"}), 400
    elif subject is None or isinstance(subject, str) is False:
        return jsonify({"error": "No subject provided"}), 400
    elif year_of_study is None or isinstance(year_of_study, int) is False:
        return jsonify({"error": "No year of study provided"}), 400
    elif country is None or isinstance(country, str) is False:
        return jsonify({"error": "No country provided"}), 400
    elif dificulty_level is None or isinstance(dificulty_level, str) is False:
        return jsonify({"error": "No dificulty level provided"}), 400
    elif topic is None or isinstance(topic, str) is False:
        return jsonify({"error": "No topic provided"}), 400


    prompt = f"""Generate a detailed study plan for a single day based on the following input:

{{
  "subject": {subject},
  "year_of_study": {year_of_study},
  "day_number": {day},
  "topic": {topic},
  "difficulty_level": {dificulty_level},
  "country": {country}
}}

Input field explanations:
- subject: The main area of study, determining the overall context.
- year_of_study: The year level of the student (e.g., 2 means second year of high school). This helps in determining the appropriate difficulty and depth of the topics.- day_number: The sequential number of this study session within the overall plan.
- topic: The specific subject to be covered in this study session.
- difficulty_level: Indicates the expected challenge level of the material.
- country: The country where the student is studying, which may influence content and examples.

Please provide the output in the following JSON format:

{{
  "day_plan": {{
    "learning_objectives": [
      "string",
      // ... list 3-5 specific learning objectives for this day
    ],
    "study_materials": {{
      "introduction": "string (about 50 words)",
      "main_content": "string (about 300 words)",
      "summary": "string (about 50 words)"
    }},
    "resources": [
      {{
        "type": "string (e.g., 'Video', 'Article', 'Book Chapter')",
        "title": "string",
      }},
      // ... list 2-3 resources
    ],
    "practice_problems": [
      {{
        "question": "string",
        "answer": "string"
      }},
      // ... list 2-3 practice problems
    ],
    "additional_notes": "string (any extra tips or context, about 50 words)"
  }}
}}

Output field explanations:
- learning_objectives: Specific goals for this study session.
- study_materials: The main content to be studied.
  - introduction: A brief overview of the topic.
  - main_content: The core material to be learned.
  - summary: A concise recap of the key points.
- resources: Additional materials for further study or reference.
- practice_problems: Example questions to test understanding.
- additional_notes: Any extra information or tips relevant to the day's study.

Ensure that the plan:
1. Is appropriate for the specified year of study and difficulty level.
2. Focuses specifically on the given topic, providing depth and detail.
3. Includes a mix of theoretical explanations and practical applications.
4. Provides clear, concise, and informative content in each section.
5. Offers activities and problems that reinforce the day's learning objectives.
6. Takes into account any relevant educational approaches or standards common in the country.

The content should be detailed enough to guide a study session of approximately 30-100 minutes, providing a comprehensive overview of the day's topic."""

    try:
        response = model.generate_content(prompt)
        return jsonify({"day_details": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/explain_topic', methods=['POST'])
def explain_topic():
    data = request.json
    topic = data.get('topic')

    if not topic:
        return jsonify({"error": "No topic provided"}), 400

    prompt = f"Explain the following topic in detail, suitable for a student who doesn't understand it: {topic}"

    try:
        response = model.generate_content(prompt)
        return jsonify({"explanation": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200


if __name__ == '__main__':
    app.run(debug=True)