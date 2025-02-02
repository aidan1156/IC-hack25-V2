import base64
import anthropic
import pdfplumber
import os
import json

def pdf_to_text_pdfplumber(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def tmp_pdf_to_string():
    # Get the first PDF file from tmp directory
    tmp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tmp')
    pdf_files = [f for f in os.listdir(tmp_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        raise Exception("No PDF files found in tmp directory")
        
    pdf_path = os.path.join(tmp_dir, pdf_files[0])
    return pdf_to_text_pdfplumber(pdf_path)

# # Usage
# file_content = tmp_pdf_to_string()

API_KEY = os.environ.get('IC_Claude')
# print(os.environ['IC_Claude'])
client = anthropic.Anthropic(
    api_key=API_KEY
)


graph_xml_prompt = """
<conceptMappingPrompt>
    <description>
        Generate only the Mermaid.js diagram code. The diagram must:
        1. Start with 'graph TD'
        2. Not use subgraphs
        3. Include only the code, no explanations
    </description>
    
    <structure>
        <mermaidSyntax>
            <styleDefinitions>
                <classDef name="fundamental" fill="transparent" stroke="#4A76E9"/>
                <classDef name="basic" fill="transparent" stroke="#B4E5A2"/>
                <classDef name="advanced" fill="transparent" stroke="#F2AA84"/>
                <classDef name="novel" fill="transparent" stroke="#C00000"/>
            </styleDefinitions>
            
            <levels>
                <level name="Core Foundations">
                    <node id="node1" label="Concept Name"/>
                    <node id="node2" label="Math Foundation"/>
                </level>
                
                <level name="Key Components">
                    <node id="node3" label="Core Technique"/>
                    <node id="node4" label="Base Theory"/>
                </level>
                
                <level name="Advanced Elements">
                    <node id="node5" label="Novel Method"/>
                    <node id="node6" label="Optimization"/>
                </level>
            </levels>
            
            <dependencies>
                <dependency from="node2" to="node3" type="direct"/>
                <dependency from="node1" to="node4" type="direct"/>
                <dependency from="node3" to="node5" type="implicit"/>
                <dependency from="node4" to="node6" type="bidirectional"/>
            </dependencies>
            
            <styling>
                <class node="node1" style="fundamental"/>
                <class node="node3" style="basic"/>
                <class node="node5" style="advanced"/>
            </styling>
        </mermaidSyntax>

          
            <example>
                %% Core Foundations
                graph TD
                    baseline[Claude 3.5 Sonnet Baseline]
                    eval[Evaluation Methods]
                    safety[Safety Framework]

                %% Key Components    
                    computer[Computer Use Capability]
                    vision[Vision Understanding]
                    reasoning[Reasoning & QA]
                    agent[Agentic Behavior]

                %% Style Definitions
                classDef fundamental fill:transparent,stroke:#4A76E9
                classDef basic fill:transparent,stroke:#B4E5A2
                classDef advanced fill:transparent,stroke:#F2AA84
                classDef novel fill:transparent,stroke:#C00000

                %% Advanced Elements
                    redteam[Red Team Testing]
                    benchmarks[Benchmark Results]
                    rsp[Responsible Scaling]

                %% Dependencies
                    baseline --> computer
                    baseline --> vision
                    baseline --> reasoning
                    eval --> benchmarks
                    eval --> redteam
                    safety --> rsp
                    computer -.-> agent
                    reasoning === agent
                    vision --> benchmarks
                    agent --> redteam

                %% Apply styles
                    class baseline,eval,safety fundamental
                    class computer,vision,reasoning,agent basic
                    class redteam,benchmarks,rsp advanced
                    class computer novel

                %% Tooltips
                    baseline[Claude 3.5 Sonnet Baseline<br><i>Original model capabilities</i>]
                    computer[Computer Use Capability<br><i>New GUI interaction skills</i>]
                    agent[Agentic Behavior<br><i>Autonomous task completion</i>]
            </example>

    </structure>
    
    <taskRequirements>
        <hierarchyLevels>
            <level name="Fundamental" description="Mathematical prerequisites & domain foundations"/>
            <level name="Basic" description="Core paper components built on fundamentals"/>
            <level name="Advanced" description="Novel contributions & complex implementations"/>
        </hierarchyLevels>
        
        <dependencyMapping>
            <relationship type="direct" symbol="-->"/>
            <relationship type="implicit" symbol="-.->"/>
            <relationship type="bidirectional" symbol="==="/>
        </dependencyMapping>
        
        <nodeRequirements>
            <level name="Fundamental" min="3" max="5"/>
            <level name="Basic" min="4" max="6"/>
            <level name="Advanced" min="2" max="4"/>
            <novelConcepts min="1" max="2"/>
        </nodeRequirements>
        
        <tooltipIntegration>
            <description maxWords="12" focus="functional purpose"/>
        </tooltipIntegration>
        
        <validationChecklist>
            <item>No orphaned nodes</item>
            <item>Consistent abstraction levels</item>
            <item>Novel contributions clearly marked</item>
            <item>Logical top-to-bottom flow</item>
        </validationChecklist>
    </taskRequirements>
    
    <outputInstructions>
        <syntaxOrder>
            <step>Define class styles first</step>
            <step>Declare all nodes</step>
            <step>Specify dependencies</step>
            <step>Apply styling classes</step>
            <step>Add tooltips last</step>
        </syntaxOrder>
        
        <formattingRules>
            <rule>Include %% comments separating diagram sections</rule>
            <rule>Alphabetize concepts within each level</rule>
            <rule>Use clean node IDs (e.g., linalg vs linear_algebra)</rule>
            <rule>Prefer terse labels with full terms in tooltips</rule>
        </formattingRules>
    </outputInstructions>
</conceptMappingPrompt>
"""

summary_xml_prompt = """
<prompt>
    <task>Extract and summarize information</task>
    <context>
        <document>Provided PDF</document>
        <subtopic>{SUBTOPIC}</subtopic>
    </context>
    <instructions>
        <requirement>Generate a summary of the provided PDF content. Get straight to the summary. No introduction.</requirement>
        <requirement>Identify and summarize all major points related to the subtopic.</requirement>
        <requirement>Ensure the summary is detailed, coherent, and logically structured.</requirement>
        <requirement>Avoid bullet points; present the information in well-formed paragraphs.</requirement>
        <requirement>Preserve the technical accuracy and key insights of the PDF content.</requirement>
        <requirement>Add a new line between each paragraph.</requirement>
    </instructions>
    <format>
        <style>Formal and explanatory</style>
        <length>Comprehensive</length>
    </format>
</prompt>
"""

quiz_xml_prompt = """
<prompt>
    <task>Generate quiz questions and answers</task>
    <context>
        <document>Provided PDF</document>
        <subtopic>{SUBTOPIC}</subtopic>
        <difficulty>{DIFFICULTY}</difficulty>
    </context>
    <instructions>
        <requirement>Generate exactly 1 quiz questions about the subtopic</requirement>
        <requirement>Cover different aspects and concepts within the subtopic</requirement>
        <requirement>Include questions of given difficulty{DIFFICULTY}, where the range of difficulty(1-5)</requirement>
        <requirement>Ensure questions are clear and unambiguous</requirement>
        <requirement>Provide complete and technically accurate answers</requirement>
        <requirement>Format output as valid JSON array of question objects</requirement>
    </instructions>
    <format>
        <structure>
            {
              "questions": [
                {
                  "question": "Question text",
                  "correct_answer": "Complete answer",
                  "difficulty": "Difficulty level (1-5)"
                }
              ]
            }
        </structure>
        <difficultyLevels>
            <level value="1">Basic recall and understanding</level>
            <level value="2">Simple application of concepts</level>
            <level value="3">Analysis and comparison</level>
            <level value="4">Complex problem solving</level>
            <level value="5">Advanced synthesis and evaluation</level>
        </difficultyLevels>
    </format>
    <validation>
        <rule>Questions must be derived from the source material</rule>
        <rule>Answers must maintain technical accuracy</rule>
        <rule>Output must be valid JSON format only</rule>
        <rule>No additional text or explanations outside JSON</rule>
    </validation>
</prompt>
"""

answer_comparison_xml_prompt = """
<prompt>
    <task>Compare student answer with correct answer and provide user-friendly feedback</task>
    <context>
        <question>{QUESTION}</question>
        <studentAnswer>{STUDENT_ANSWER}</studentAnswer>
        <correctAnswer>{CORRECT_ANSWER}</correctAnswer>
        <questionDifficulty>{DIFFICULTY}</questionDifficulty>
    </context>
    <instructions>
        <requirement>Compare the semantic meaning of the answers, not just exact matches</requirement>
        <requirement>Consider technical accuracy and completeness</requirement>
        <requirement>Generate a confidence score between 0 and 1</requirement>
        <requirement>Provide emoji rating based on score:
            - ⭐⭐⭐ for correct
            - ⭐⭐ for partially correct
            - ⭐ for needs improvement
        </requirement>
        <requirement>List only the key points missed or incorrect, if any</requirement>
        <requirement>Keep feedback concise and constructive</requirement>
        <requirement>Format output as valid JSON only</requirement>
        <requirement>Add a new line between each point</requirement>
        <requirement>Make sure the stars are included in the feedback</requirement>
    </instructions>
    <format>
        <structure>
            {
                "confidence_score": float,
                "feedback": "⭐⭐⭐ Great work! [or] Here are the key points to review:"
            }
        </structure>
        <feedbackGuidelines>
            <correct>
                "Great work! Your answer demonstrates full understanding."
            </correct>
            <partiallyCorrect>
                "Good attempt! Here are the key points to review:
                • [missed point 1]
                • [missed point 2]"
            </partiallyCorrect>
            <needsImprovement>
                "Let's review these important points:
                • [missed point 1]
                • [missed point 2]
                • [missed point 3]"
            </needsImprovement>
        </feedbackGuidelines>
        <scoringGuidelines>
            <difficulty level="1">
                <perfect>1.0</perfect>
                <minor_errors>0.8</minor_errors>
                <major_errors>0.4</major_errors>
            </difficulty>
            <difficulty level="2">
                <perfect>1.0</perfect>
                <minor_errors>0.6</minor_errors>
                <major_errors>0.2</major_errors>
            </difficulty>
            <difficulty level="3">
                <perfect>1.0</perfect>
                <minor_errors>0.6</minor_errors>
                <major_errors>0.2</major_errors>
            </difficulty>
            <difficulty level="4">
                <perfect>1.0</perfect>
                <minor_errors>0.4</minor_errors>
                <major_errors>0.2</major_errors>
            </difficulty>
            <difficulty level="5">
                <perfect>1.0</perfect>
                <minor_errors>0.2</minor_errors>
                <major_errors>0.1</major_errors>
            </difficulty>
        </scoringGuidelines>
    </format>
    <validation>
        <rule>Score must be between 0 and 1</rule>
        <rule>Feedback must be constructive and specific</rule>
        <rule>Higher difficulty questions should be graded more leniently</rule>
        <rule>Output must be valid JSON format only</rule>
        <rule>Always include appropriate emoji rating</rule>
    </validation>
</prompt>
"""

question_xml_prompt = """
<prompt>
    <task>Answer user question about the document content</task>
    <context>
        <document>Provided PDF</document>
        <topic>{TOPIC}</topic>
        <question>{QUESTION}</question>
    </context>
    <instructions>
        <requirement>Provide a clear, direct answer to the user's question</requirement>
        <requirement>Base answers on the document content</requirement>
        <requirement>Use natural, conversational language while maintaining technical accuracy</requirement>
        <requirement>Break down complex concepts into understandable explanations</requirement>
        <requirement>Include relevant examples or analogies when helpful</requirement>
        <requirement>Keep responses focused and concise</requirement>
        <requirement>Add line breaks between paragraphs for readability</requirement>
        <requirement>Get straight to the answer, do not include any other text like "Based on the document" or "Here is the answer to your question"</requirement>
    </instructions>
    <format>
        <guidelines>
            <style>Conversational but professional</style>
            <length>2-3 paragraphs maximum</length>
            <formatting>Use line breaks between paragraphs</formatting>
        </guidelines>
    </format>
    <validation>
        <rule>Answer should try to be derived from document content</rule>
        <rule>Response should be complete but concise</rule>
    </validation>
</prompt>
"""

# Send to Claude
def queryClaude(file_content, query, topic=None, difficulty=None):
    prompt = [
        {
            "type": "text",
            "text": file_content
        }
    ]
    
    if topic:
        # Replace placeholder in summary XML prompt with specific topic
        formatted_query_pre = query.replace("{SUBTOPIC}", topic)
    else:
        formatted_query_pre = query

    if difficulty:
        # Replace placeholder in summary XML prompt with specific topic
        formatted_query = formatted_query_pre.replace("{DIFFICULTY}", difficulty)
    else:
        formatted_query = formatted_query_pre
        
    prompt.append({
        "type": "text",
        "text": formatted_query
    })

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        messages=[
            {
                "role": "user", 
                "content": prompt
            }
        ]
    )
    return message.content


# ======= hardcord testing ==========

# message_content = queryClaude(file_content, xml_prompt)

def extract_text(text):
    if isinstance(text, list):
        text = text[0].text if text else ""
    return text

def save_json_to_file(json_string, filename):
    """Save JSON string to a file in the tmp directory"""
    try:
        json_data = json.loads(json_string)  # Parse the JSON string
        file_path = os.path.join('tmp', filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)
            
        return file_path
    except Exception as e:
        print(f"Error saving JSON to file: {e}")
        return None
# mermaid_code = extract_mermaid_code(message_content)
# print(mermaid_code)