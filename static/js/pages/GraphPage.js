import { Page } from "./Page.js"

export class GraphPage extends Page {
    constructor() {
        super("graph-page")
    }

    show(response) {
        super.show()
        window.assistant.topBarController.hide()
        if (response) {

        //     response.mermaid = `
        //         graph TD
        // %% Style Definitions
        // classDef fundamental fill:#e1f5fe,stroke:#01579b
        // classDef basic fill:#f3e5f5,stroke:#4a148c
        // classDef advanced fill:#e8f5e9,stroke:#1b5e20
        // classDef novel fill:#fce4ec,stroke:#880e4f
    
        // %% Core Foundations
        // pyth[Pythagorean Theorem]
        // number[Number Theory]
        // pattern[Pattern Recognition]
    
        // %% Key Components
        // formula[Triple Generation Formula]
        // oddeven[Odd-Even Classification]
        // validation[Result Validation]
        // coding[Python Implementation]
    
        // %% Advanced Elements
        // crypto[Cryptographic Applications]
        // visual[Visual Analytics]
        // optimize[Formula Optimization]
    
        // %% Dependencies
        // pyth --> formula
        // number --> formula
        // pattern --> oddeven
        // formula --> crypto
        // oddeven -.-> optimize
        // validation === coding
        // formula --> visual
        // coding --> crypto
        // visual --> optimize
    
        // %% Apply styles
        // class pyth,number,pattern fundamental
        // class formula,oddeven,validation,coding basic
        // class crypto,visual,optimize advanced
        // class coding novel
    
        // %% Tooltips
        // pyth[Pythagorean Theorem<br><i>Core mathematical foundation</i>]
        // formula[Triple Generation Formula<br><i>Novel method for generating triples</i>]
        // crypto[Cryptographic Applications<br><i>Security implementations</i>]
        //     `
            window.assistant.orbController.removeAll()
            
            const graphDiv = document.querySelector('#graph-page')
            graphDiv.innerHTML = `<div class="mermaid">${response.mermaid}</div>`
            
            mermaid.contentLoaded()
    
            setTimeout(() => {
                document.querySelectorAll('#graph-page svg .nodeLabel').forEach(node => {
                    node.onclick = () => {
                        window.assistant.summariseTopicPage.show(node.querySelector('p').innerText)
                    }
                })
            }, 1000)
        }
    }
}