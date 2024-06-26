export function update(ctx, documentation) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Draws squares for groups
    // TODO This calculation should not be done each frame
    let groups = documentation.map(item => item.groups);
    let uniqueGroups = [...new Set(groups)];

    uniqueGroups.forEach(function(group) {
        let filteredSquares = documentation.filter(item => item.groups === group);

        // Initialize variables for minimum and maximum coordinates
        let minX = Number.MAX_VALUE;
        let minY = Number.MAX_VALUE;
        let maxX = Number.MIN_VALUE;
        let maxY = Number.MIN_VALUE;

        filteredSquares.forEach(function(square) {
            // Update minimum and maximum x coordinates
            minX = Math.min(minX, square.viz.x);
            maxX = Math.max(maxX, square.viz.x);

            // Update minimum and maximum y coordinates
            minY = Math.min(minY, square.viz.y);
            maxY = Math.max(maxY, square.viz.y);
        });
        ctx.fillStyle = "grey";
        ctx.fillRect(minX, minY, maxX - minX + 70, maxY - minY + 70);
    });

    // Draws icons
    documentation.forEach(function(square) {

        
        if(square.active) {
            ctx.fillStyle = "blue";
            ctx.fillRect(square.viz.x, square.viz.y, 50,50);
        } else {
            var icon = new Image();
            icon.src = square.icon;
            ctx.drawImage(icon, square.viz.x, square.viz.y, 50, 50);
        }

        ctx.fillStyle = "black";
        ctx.font = "12px Consolas";
        ctx.fillText(square.id, square.viz.x + 20, square.viz.y + 70);
        
        // Draw arrows from parent squares
        square.parents.forEach(function(parentId) {
            var parentSquare = documentation.find(function(square) {
                return square.id === parentId;
            });
            
            if (parentSquare) {


                // Calculate the midpoint between the parent square and the current square

                var diffX = parentSquare.viz.x - square.viz.x
                var diffY = parentSquare.viz.y - square.viz.y
                var midX = (parentSquare.viz.x + square.viz.x) / 2;
                var midY = (parentSquare.viz.y + square.viz.y) / 2;

                var startX, startY
                var endX, endY
                // Drawing lines. probably not optimal and should be cached not calculated every time
                ctx.beginPath();
                if (Math.abs(diffX) < Math.abs(diffY)) {
                    //First line vertical

                    // Check start square
                    if (diffY > 0) {
                        startX = parentSquare.viz.x + 25 //point to the TOP
                        startY = parentSquare.viz.y
                    } else {
                        startX = parentSquare.viz.x + 25 //point to the BOTTOM
                        startY = parentSquare.viz.y + 50
                    }
                    // Check end square
                    if (diffX > 0) {
                        
                        endX = square.viz.x + 50 //point to the LEFT
                        endY = square.viz.y + 25
                    } else {
                        endX = square.viz.x //point to the RIGHT
                        endY = square.viz.y + 25
                    }
                    ctx.moveTo(startX, startY);
                    ctx.lineTo(startX, midY);
                    ctx.lineTo(endX,endY)
                } else {
                    //First line horizontal
                    if (diffX > 0) {
                        
                        startX = parentSquare.viz.x //point to the LEFT
                        startY = parentSquare.viz.y + 25
                        ctx.moveTo(startX, startY);
                    } else {
                        startX = parentSquare.viz.x + 50//point to the RIGHT
                        startY = parentSquare.viz.y + 25
                        ctx.moveTo(startX, startY);
                    }
                    // Check end square
                    if (diffY > 0) {
                        endX = square.viz.x + 25 //point to the BOTTOM
                        endY = square.viz.y + 50
                    } else {
                        endX = square.viz.x +25 //point to the TOP
                        endY = square.viz.y
                    }
                    ctx.moveTo(startX, startY);
                    ctx.lineTo(midX, startY);
                    ctx.lineTo(endX,endY)
                }
                
                
                ctx.strokeStyle = "black";
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.beginPath();
                ctx.arc(endX, endY, 5, 0, 2 * Math.PI);
                ctx.fillStyle = "black";
                ctx.fill();
                ctx.closePath();
            }
        });
    });
    requestAnimationFrame(() => update(ctx, documentation));
}