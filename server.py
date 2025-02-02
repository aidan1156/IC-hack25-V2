from flask import Flask, render_template, request, send_from_directory, make_response
import json
import os
import time
import tts
from pdfer import tmp_pdf_to_string, queryClaude, extract_text, graph_xml_prompt, summary_xml_prompt, quiz_xml_prompt, answer_comparison_xml_prompt, save_json_to_file, question_xml_prompt

app = Flask(__name__,static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'tmp/'
main_dir = os.path.dirname(os.path.realpath(__file__))

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload-documents', methods=['GET', 'POST'])
def uploadFile():
    # Clearing out tmp directory before saving new files
    UPLOAD_DIR = main_dir + '/tmp/'
    for filename in os.listdir(UPLOAD_DIR):
        try:
            if os.path.isfile(UPLOAD_DIR + filename):
                os.unlink(UPLOAD_DIR + filename)
        except Exception as e:
            print(f"Error deleting {filename}: {e}")

    # saving the new files
    i = 0
    mermaid_code = ""
    while ('file'+str(i) in request.files):
        file = request.files['file'+str(i)]
        file.save(UPLOAD_DIR + file.filename)
        
        # Process PDF after saving
        try:
            file_content = tmp_pdf_to_string()
            message_content = queryClaude(file_content, graph_xml_prompt)
            mermaid_code = extract_text(message_content)
        except Exception as e:
            print(f"Error processing PDF: {e}")
        
        i += 1
    
    # time.sleep(2)
    
    return json.dumps({
        'status': 'done',
        'mermaid': mermaid_code
    })

@app.route('/get-summary', methods=['POST'])
def get_summary():
    data = request.get_json()
    topic = data['topic']
    
    try:
        file_content = tmp_pdf_to_string()
        summary = extract_text(queryClaude(file_content, summary_xml_prompt, topic))

        tts.speak(summary)
        return json.dumps({
            'summary': summary
        })
    except Exception as e:
        print(f"Error generating summary: {e}")
        return json.dumps({
            'summary': f"Error generating summary for {topic}"
        }), 500

@app.route('/ask-question', methods=['POST'])
def askQuestion():
    try:
        data = request.get_json()
        question = data.get('question', '')
        topic = data.get('topic', '')
        
        # Get file content for context
        file_content = tmp_pdf_to_string()
        
        # Format the prompt with the question and topic
        formatted_prompt = question_xml_prompt.replace("{QUESTION}", question)\
            .replace("{TOPIC}", topic)
            
        # Get response from Claude
        answer_text = extract_text(queryClaude(file_content, formatted_prompt))
        tts.speak(answer_text)
        return json.dumps({
            'answer': answer_text
        })
        
    except Exception as e:
        print(f"Error processing question: {e}")
        return json.dumps({
            'answer': 'Sorry, I had trouble processing that question.'
        }), 500

@app.route('/get-quiz-qu', methods=['POST'])
def getQuizQu():
    # return json.dumps({
    #     'question': 'dsfsd',
    #     'difficulty': 0
    # })
    try:
        with open(os.path.join(main_dir, 'tmp', 'user_context.json'), 'r') as file:
            user_context = json.load(file)
            difficulty = user_context['user_confidence']

        # Create tmp directory if it doesn't exist
        tmp_dir = os.path.join(main_dir, 'tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
            
        # If qs.json doesn't exist or is empty, generate new questions
        qs_path = os.path.join(tmp_dir, 'qs.json')
        if not os.path.exists(qs_path):
            file_content = tmp_pdf_to_string()
            topic = request.get_json()['topic']
            questions = extract_text(queryClaude(file_content, quiz_xml_prompt, topic, str(int(difficulty))))
            save_json_to_file(questions, "qs.json")
            
        # Load questions from file
        with open(qs_path, 'r') as file:
            data = json.load(file)
            
        if not data or not data.get('questions'):
            # If no questions left, get new ones from Claude
            file_content = tmp_pdf_to_string()
            topic = request.get_json()['topic']
            questions = extract_text(queryClaude(file_content, quiz_xml_prompt, topic, str(int(difficulty))))
            save_json_to_file(questions, "qs.json")
            
            # Reload the new questions
            with open(qs_path, 'r') as file:
                data = json.load(file)

        # Get the first question and remove it from the list
        question = data['questions'][0]
        
        # Save updated questions back to file
        with open(qs_path, 'w') as file:
            json.dump(data, file)

        tts.speak(question['question'])
        
        return json.dumps({
            'question': question['question'],
            'difficulty': question['difficulty']
        })
        
    except Exception as e:
        print(f"Error getting quiz question: {e}")
        return json.dumps({
            'question': 'Error getting question',
            'difficulty': 1
        })

@app.route('/set-confidence', methods=['POST'])
def setConfidence():
    data = json.loads(request.data)
    confidence = data['confidence']

    # Save confidence in json file
    file_dir = os.path.join(main_dir, 'tmp', 'user_context.json')
    with open(file_dir, 'w') as file:
        json.dump({'user_confidence': float(confidence)}, file)

    return json.dumps({
        'state': 'done'
    })


@app.route('/check-answer', methods=['POST'])
def getQuizFeedback():
    try:
        data = request.get_json()
        student_answer = data.get('answer', '')
        question = data.get('question', '')
        
        # Read the questions file to get the correct answer
        qs_path = os.path.join(main_dir, 'tmp', 'qs.json')
        with open(qs_path, 'r') as file:
            questions_data = json.load(file)
            
        # Find the matching question and get its correct answer
        correct_answer = None
        difficulty = 1
        for q in questions_data['questions']:
            if q['question'] == question:
                correct_answer = q['correct_answer']
                difficulty = q['difficulty']
                break
                
        if not correct_answer:
            raise Exception("Question not found")
            
        # Get file content for context
        file_content = tmp_pdf_to_string()
            
        # Compare answers using Claude
        comparison_prompt = answer_comparison_xml_prompt.replace("{QUESTION}", question)\
            .replace("{STUDENT_ANSWER}", student_answer)\
            .replace("{CORRECT_ANSWER}", correct_answer)\
            .replace("{DIFFICULTY}", str(difficulty))
            
        feedback_response = extract_text(queryClaude(file_content, comparison_prompt))
        feedback_data = json.loads(feedback_response)
        print(feedback_data)
        
        feedback_text = feedback_data['feedback']
        tts.speak(feedback_text)

        questions_data['questions'].pop(0)
        with open(qs_path, 'w') as file:
            json.dump(questions_data, file)

        user_context_path = os.path.join(main_dir, 'tmp', 'user_context.json')
        with open(user_context_path, 'r') as file:
            user_context = json.load(file)
        
        user_context['user_confidence'] += float(difficulty) * float(feedback_data['confidence_score'])
        print(user_context)
        with open(user_context_path, 'w') as file:
            json.dump(user_context, file, indent=4)
        
        return json.dumps({
            'feedback': feedback_text,
            'score': feedback_data['confidence_score']
        })
        
    except Exception as e:
        print(f"Error checking answer: {e}")
        return json.dumps({
            'feedback': 'Error evaluating answer',
            'score': 0
        })


@app.route('/speech-to-text', methods=['POST'])
def speechToText():
    file = request.files['audio']
    file.save(main_dir + '/tmp.wav')

    try:
        text= tts.understand(main_dir + '/tmp.wav')
    except:
        text = ''

    return json.dumps({
        'transcript': text
    })

@app.route('/service-worker.js')
def serviceworker():
    response=make_response(send_from_directory('static','service-worker.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5003)