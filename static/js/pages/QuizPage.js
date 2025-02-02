import {Page} from './Page.js'
import { postRequest, fadeText } from '../utils.js'
import { AudioManager } from "../audio.js"


export class QuizPage extends Page {
    constructor() {
        super("quiz-page")

        this.question;
        this.feedback;

        this.topic;

        this.audioManager = new AudioManager(document.querySelector('#quiz-page'))
    }

    show(topic) {
        super.show()
        this.topic = topic

        window.assistant.topBarController.setTopic(this.topic)

        window.assistant.buttonController.setButtons([
            {
                'text': 'Start Quiz',
                'onclick': () => {
                    postRequest('/set-confidence', {
                        'confidence': document.querySelector('#quiz-understanding').value,
                    }).then((response) => {
                        document.querySelector('#quiz-page .input-mic').classList.remove('hidden')
                        document.querySelector('#quiz-understanding').classList.add('hidden')
                        this.showQuizQuestion()
                    })
                }
            }
        ])
        document.querySelector('#quiz-page .input-mic').classList.add('hidden')
        document.querySelector('#quiz-understanding').classList.remove('hidden')
        document.querySelector('#quiz-page .assistant-text').innerHTML = 'What is your confidence in this topic?'

        this.audioManager.setup(
            document.querySelector('#quiz-record-button'),
            document.querySelector('#quiz-answer'),
            this.submitAnswer.bind(this)
        )
    }

    showQuizQuestion() {
        document.querySelector('#quiz-page .input-mic').classList.add('hidden')
        document.querySelector('#quiz-page .assistant-text').innerHTML = ''
        window.assistant.buttonController.setButtons([])

        window.assistant.orbController.setThinking()
        postRequest('/get-quiz-qu', {'topic': this.topic}).then((response) => {
            window.assistant.orbController.removeAll()
            window.assistant.buttonController.setButtons([
                {
                    'text': 'Submit',
                    'onclick': () => {
                        this.submitAnswer()
                    }
                }
            ])

            response = JSON.parse(response)
            document.querySelector('#quiz-page .input-mic').classList.remove('hidden')
            setTimeout(() => {
                window.assistant.orbController.removeAll()
            }, 2000)
            this.question = response['question']

            window.assistant.speak.speak()
            fadeText(document.querySelector('#quiz-page .assistant-text'), this.question)
            // document.querySelector('#quiz-page .assistant-text').innerHTML = this.question
        }).catch((error) => {
            console.log(error)
        })
    }

    submitAnswer() {
        let answer = document.querySelector('#quiz-answer').value
        if (!answer.trim()) return;

        document.querySelector('#quiz-page .input-mic').classList.add('hidden')
        document.querySelector('#quiz-page .assistant-text').innerHTML = 'Evaluating your answer...'

        window.assistant.orbController.setThinking()
        postRequest('/check-answer', {
            'topic': this.topic,
            'question': this.question,
            'answer': answer
        }).then((response) => {
            response = JSON.parse(response)
            this.feedback = response['feedback']

            document.querySelector('#quiz-answer').value = ''

            window.assistant.speak.speak()
            fadeText(document.querySelector('#quiz-page .assistant-text'), this.feedback)
            // document.querySelector('#quiz-page .assistant-text').innerHTML = this.feedback
            window.assistant.orbController.removeAll()
            window.assistant.buttonController.setButtons([
                {
                    'text': 'Next Question',
                    'onclick': () => {
                        this.showQuizQuestion()
                    }
                }
            ])
        }).catch((error) => {
            console.log(error)
        })
        
        window.assistant.buttonController.setButtons([])
    }
}