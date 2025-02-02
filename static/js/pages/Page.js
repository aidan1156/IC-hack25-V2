

export class Page {
    constructor(id) {
        this.id = id
    }

    show() {
        window.assistant.buttonController.setButtons([])

        document.querySelectorAll('.page').forEach(page => {
            page.classList.add('hidden')
        })

        document.querySelector(`#${this.id}`).classList.remove('hidden')
    }
}