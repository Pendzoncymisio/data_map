var canvas = document.getElementById('canvas');
import { state } from './state.js';

import { setupCanvasEvents } from './canvasEvents.js';
import { update } from './update.js';

window.addEventListener('resize', function() {
    canvas.width = window.innerWidth * (2 / 3);
    canvas.height = window.innerHeight;
    // Redraw your canvas here after resizing
});

window.addEventListener('load', function() {
    canvas.width = window.innerWidth * (2 / 3);
    canvas.height = window.innerHeight;
});

var ctx = canvas.getContext('2d');




// Get file with documentation that needs to be visualized. Can be separate function
//Not defined propery "active", false by default
var documentation; // Declare the documentation variable outside the fetch function



fetch('documentation.json')
    .then(response => response.json())
    .then(data => {
        documentation = processDocumentation(data); // Call the function that depends on the fetched data
        console.log(documentation);
        
    })
    .then(() => {
        setupCanvasEvents(canvas, documentation);
    })
    .then(() => {
        requestAnimationFrame(() => update(ctx, documentation));
    })
    .catch(error => console.error('Error:', error));

function processDocumentation(documentation) {
    return documentation.map((document, index) => {
        if (document.id === undefined) {
            throw new Error("ID field is missing in" ,index,"th element");
        }
        return {
            id: document.id,
            icon: document.icon !== undefined ? document.icon : "default_icon",
            description: document.description !== undefined ? document.description : "default_icon",
            parents: document.parents !== undefined ? document.parents : [],
            groups: document.groups !== undefined ? document.groups : [],
            show_level: document.show_level !== undefined ? document.show_level : 1,
            viz: document.viz !== undefined ? document.viz : {x: 0,y: 0, size:50},
        }
    });

    // Rest of the code that depends on the processed documentation
}

function saveDocumentation() {
    localStorage.setItem('documentation', JSON.stringify(documentation));
}

function loadDocumentation() {
    var retrievedData = localStorage.getItem('documentation');
    documentation = JSON.parse(retrievedData);
}
    
function updateDocumentation() {
    // Get the user input from the squareProperties field
    var userInput = document.getElementById('squareProperties').value;
    var userInputParsed = JSON.parse(userInput);
    // Update the active square's description with the user input
    if (activeSquare) {
        let activeSquareIndex = documentation.findIndex(square => square.id === activeSquare.id);
        documentation[activeSquareIndex] = userInputParsed;
    }
}

 