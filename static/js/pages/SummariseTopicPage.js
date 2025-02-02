import {Page} from './Page.js'
import { postRequest, fadeText } from '../utils.js'


export class SummariseTopicPage extends Page {
    constructor() {
        super("topic-page")

        this.topic;
    }

    show(topic) {
        super.show()
        this.topic = topic

        window.assistant.topBarController.setTopic(this.topic)

        this.showSummaryPage()
        document.querySelector('#topic-page .assistant-text').innerHTML = ''
    }

    showSummaryPage() {
        window.assistant.orbController.setThinking()
        postRequest('/get-summary', {'topic': this.topic}).then((response) => {
            window.assistant.orbController.removeAll()
            window.assistant.buttonController.setButtons([
                {
                    'text': 'I have a question',
                    'onclick': () => {
                        window.assistant.questionPage.show(this.topic)
                    }
                },
                {
                    'text': 'Quiz me',
                    'onclick': () => {
                        window.assistant.quizPage.show(this.topic)
                    }
                }
            ])
            
            response = JSON.parse(response)
            this.summary = response['summary']
            window.assistant.speak.speak()
            fadeText(document.querySelector('#topic-page .assistant-text'), this.summary)
            // innerHTML = this.summary
        }).catch((error) => {
            console.log(error)
        })
        
    }
}