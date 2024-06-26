import { activateSquare, deactivateAllSquares } from './activations.js';

function getPosition(el) {
    var xPosition = 0;
    var yPosition = 0;

    while (el) {
        xPosition += (el.offsetLeft - el.scrollLeft + el.clientLeft);
        yPosition += (el.offsetTop - el.scrollTop + el.clientTop);
        el = el.offsetParent;
    }
    return {
        x: xPosition,
        y: yPosition
    };
}

function getMouseRelPosition(e) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
    };
}

/**
 * Returns the square that was clicked based on the mouse coordinates. Retuns null when clicked outside all squares.
 * @param {Object} mouse - The mouse object containing the x and y coordinates.
 * @returns {Object|null} - The clicked square object or null if no square was clicked.
 */
function getClickedSquare(mouse, documentation) {
    console.log(documentation);
    var clickedSquare = null;
    documentation.forEach(function(square) {
        if (mouse.x > square.viz.x && mouse.x < square.viz.x + square.viz.size && mouse.y > square.viz.y && mouse.y < square.viz.y + square.viz.size) {
            clickedSquare = square;
        }
    });
    return clickedSquare;
}

const canvasPos = getPosition(canvas);
var mouseX = 0;
var mouseY = 0;
var dragViewport = false;
var viewportX, viewportY;

export function setupCanvasEvents(canvas, documentation) {
    canvas.addEventListener('mousedown', function (e) {
        var mouse = getMouseRelPosition(e);
        var clickedSquare = getClickedSquare(mouse, documentation);
        
        if (clickedSquare) {
            clickedSquare.drag = true;
        } else {
            dragViewport = true;
            viewportX = mouse.x;
            viewportY = mouse.y;
        }
    });

    canvas.addEventListener('mouseup', function () {
        documentation.forEach(function(square) {
            square.drag = false;
        });
        dragViewport = false;
    });

    canvas.addEventListener('mousemove', function (e) {
        mouseX = e.clientX - canvasPos.x;
        mouseY = e.clientY - canvasPos.y;
        documentation.forEach(function(square) {
            if (square.drag) {
                square.viz.x = mouseX - square.viz.size / 2;
                square.viz.y = mouseY - square.viz.size / 2;
            }
        });
        if (dragViewport) {
            var dx = mouseX - viewportX;
            var dy = mouseY - viewportY;
            documentation.forEach(function(square) {
                square.viz.x += dx;
                square.viz.y += dy;
            });
            viewportX = mouseX;
            viewportY = mouseY;
        }
    });

    canvas.addEventListener("click", function (e) {
        var mouse = getMouseRelPosition(e);
        var clickedSquare = getClickedSquare(mouse, documentation);
        if(clickedSquare) {
            deactivateAllSquares();
            activateSquare(clickedSquare);
        } else {
            deactivateAllSquares();
        }
    });
}