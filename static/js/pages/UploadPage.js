
import {Page} from './Page.js'
import { postRequest } from '../utils.js'

export class UploadPage extends Page {
    constructor() {
        super("upload-page")
    }
    
    show() {
        super.show()

        window.assistant.buttonController.setButtons([
            {
                'text': 'Upload',
                'onclick': () => {
                    this.uploadFiles()
                }
            }
        ])
    }

    updateFiles() {
        let files = document.querySelector('#files-upload').files
        document.querySelector('.upload-box').innerHTML = ''

        for (let file of files) {
            let a = document.createElement('div')
            a.innerHTML = `
                <img src="/static/icons/file.svg" alt="">
                ${file.name}
            `
            
            document.querySelector('.upload-box').appendChild(a)
        }
    }

    uploadFiles() {
        window.assistant.orbController.setThinking()
        window.assistant.buttonController.setButtons([])
        document.querySelector('.uploading-file-text').classList.remove('hidden')
        let formData = new FormData()

        let i = 0
        for (let file of document.querySelector('#files-upload').files) {
            formData.append('file' + i, file)
            i++
        }

        postRequest('/upload-documents', formData, true).then((response) => {
            window.assistant.graphPage.show(JSON.parse(response))
            window.assistant.orbController.removeAll()
        }).catch((error) => {
            console.log(error)
        })
    }
}
