
import { postRequest, fadeText } from "../utils.js"
import { Page } from "./Page.js"
import { AudioManager } from "../audio.js"

export class QuestionPage extends Page {
    constructor() {
        super("question-page")

        this.topic

        this.audioManager = new AudioManager(document.querySelector('#question-page'))
    }

    show(topic) {
        super.show()

        this.topic = topic

        window.assistant.buttonController.setButtons([
            {
                'text': 'Submit',
                'onclick': () => {
                    this.submitQuestion()
                }
            }
        ])
        this.audioManager.setup(
            document.querySelector('#question-record-button'),
            document.querySelector('#question-input'),
            this.submitQuestion.bind(this)
        )
        document.querySelector('#question-page .assistant-text').innerHTML = ''
    }

    submitQuestion() {
        let question = document.querySelector('#question-input').value
        window.assistant.orbController.setThinking()

        document.querySelector('#question-page .assistant-text').innerHTML = `Thinking about ${question}...`

        postRequest('/ask-question', {'question': question, 'topic': this.topic}).then((response) => {
            let data = JSON.parse(response)
            window.assistant.orbController.removeAll()
            fadeText(document.querySelector('#question-page .assistant-text'), data.answer)
            // document.querySelector('#question-page .assistant-text').innerHTML = data.answer
            document.querySelector('#question-input').value = ''
            document.querySelector('#question-input').placeholder = 'Ask another question...'
            window.assistant.speak.speak()

            window.assistant.buttonController.setButtons([
                {
                    'text': 'Submit',
                    'onclick': () => {
                        this.submitQuestion()
                    }
                },
                {
                    'text': 'Quiz me',
                    'onclick': () => {
                        window.assistant.quizPage.show(this.topic)
                    }
                }
            ])
        }).catch((error) => {   
            console.log(error)
        })

    }
}