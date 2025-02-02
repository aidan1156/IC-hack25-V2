export function postRequest(url, data, raw=false) {
    return new Promise((resolve, reject) => {
        fetch(url, {
            'method': 'POST',
            'headers': raw ? {} : {
                'Content-Type': 'application/json'
            },
            'body': raw ? data : JSON.stringify(data)
        }).then((response) => {
            response.text().then(text => {
                resolve(text)
            }).catch(error => {
                reject(error)
            })
        }).catch(error => {
            reject(error)
        })
    })
}


export function fadeText(element, text) {
    element.innerHTML = ''
    const textSplit = text.split(' ')
    let i = 0
    for (let word of textSplit) {
        let a = document.createElement('span')
        a.innerHTML = word + ' '
        a.style.setProperty('--delay', (i/100) + 's')
        i++
        element.appendChild(a)
    }
}