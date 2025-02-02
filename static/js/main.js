
import { UploadPage } from './pages/UploadPage.js'
import { SummariseTopicPage } from './pages/SummariseTopicPage.js'
import { QuestionPage } from './pages/QuestionPage.js'
import { GraphPage } from './pages/GraphPage.js'
import { QuizPage } from './pages/QuizPage.js'

class MainController {
    constructor() {
        this.uploadPage = new UploadPage()
        this.summariseTopicPage = new SummariseTopicPage()
        this.questionPage = new QuestionPage()
        this.graphPage = new GraphPage()
        this.quizPage = new QuizPage()

        this.buttonController = new ButtonController()
        this.orbController = new OrbController()
        this.topBarController = new TopBarController()
        this.speak = new Speak()

    }
    
    init() {
        this.uploadPage.show()
        // window.assistant.graphPage.show({})
        // this.summariseTopicPage.show("example topic")
        // this.questionPage.show("topic")
        // this.quizPage.show("rawr")
    }
}

class ButtonController {
    constructor() {
        document.addEventListener("keydown", (event) => {
            if (event.code == 'Digit1' && event.shiftKey) {
                document.querySelector('.button-options button:nth-child(1)').click()
            } else if (event.code == 'Digit2' && event.shiftKey) {
                document.querySelector('.button-options button:nth-child(2)').click()
            }
        })
    }
    setButtons(buttons) {
        document.querySelector('.button-options').innerHTML = ''

        for (let button of buttons) {
            let a = document.createElement('button')
            a.innerHTML = `
                <span class="text">${button.text}</span>
                <img src="/static/icons/next.svg" alt="">
            `
            a.onclick = button.onclick
            document.querySelector('.button-options').appendChild(a)
        }
    }
}

class OrbController {
    removeAll() {
        document.querySelector('.glowing-orb').classList.remove('thinking')
        document.querySelector('.glowing-orb').classList.remove('loading')
    }
    setLoading() {
        this.removeAll()
        document.querySelector('.glowing-orb').classList.add('loading')
    }

    setThinking() {
        this.removeAll()
        document.querySelector('.glowing-orb').classList.add('thinking')
    }
}

class TopBarController {
    hide() {
        document.querySelector('.page-header').classList.add('hidden')
    }
    show() {
        document.querySelector('.page-header').classList.remove('hidden')
    }
    setTopic(topic) {
        this.show()
        document.querySelector('.page-header h1').innerHTML = topic
    }
}

class Speak {
    constructor() {
        this.i = 0
    }
    speak() {
        this.i++
        document.querySelector('#main-audio').src = `/static/audio.mp3?refresh=${this.i}`
        setTimeout(() => {
            document.querySelector('#main-audio').play()
        }, 500)
    }
}

window.assistant = new MainController()

window.assistant.init()