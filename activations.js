import { state } from './state.js';
export function activateSquare(square) {
    square.active = true;
    state.activeSquare = square;

    var squarePropertiesInput = document.getElementById('squareProperties');
    squarePropertiesInput.value = JSON.stringify(state.activeSquare, null, 2);
}

export function deactivateAllSquares() {
    //TODO: Loop through all active when there can be all active
    if (state.activeSquare) {
        state.activeSquare.active = false;
        state.activeSquare = null;
    }
}