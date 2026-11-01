const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const box = 20;
const canvasSize = 400;
let snake = [{ x: 8 * box, y: 10 * box }];
let direction = null;
let food = randomFood();
let foodMoveCounter = 0;
const FOOD_MOVE_INTERVAL = 3; // Apple moves every 3 snake moves
let score = 0;
let gameInterval;

function randomFood() {
    return {
        x: Math.floor(Math.random() * (canvas.width / box)) * box,
        y: Math.floor(Math.random() * (canvas.height / box)) * box
    };
}

function drawSnake() {
    ctx.fillStyle = '#0f0';
    snake.forEach((segment, i) => {
        ctx.fillStyle = i === 0 ? '#7fff00' : '#0f0';
        ctx.fillRect(segment.x, segment.y, box, box);
        ctx.strokeStyle = '#111';
        ctx.strokeRect(segment.x, segment.y, box, box);
    });
}

function drawFood() {
    ctx.font = `${box * 0.9}px serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('🍎', food.x + box / 2, food.y + box / 2);
}

function moveFood() {
    // Move food to a random adjacent cell, but not onto the snake or outside bounds
    const directions = [
        { x: -box, y: 0 }, // left
        { x: box, y: 0 },  // right
        { x: 0, y: -box }, // up
        { x: 0, y: box }   // down
    ];
    // Shuffle directions for randomness
    for (let i = directions.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [directions[i], directions[j]] = [directions[j], directions[i]];
    }
    for (const dir of directions) {
        const newX = food.x + dir.x;
        const newY = food.y + dir.y;
        // Check bounds
        if (
            newX >= 0 && newX < canvas.width &&
            newY >= 0 && newY < canvas.height &&
            !snake.some(segment => segment.x === newX && segment.y === newY)
        ) {
            food.x = newX;
            food.y = newY;
            break;
        }
    }
}

function moveSnake() {
    if (!direction) return;
    const head = { ...snake[0] };
    if (direction === 'LEFT') head.x -= box;
    if (direction === 'RIGHT') head.x += box;
    if (direction === 'UP') head.y -= box;
    if (direction === 'DOWN') head.y += box;

    // Check collision with walls
    if (
        head.x < 0 || head.x >= canvas.width ||
        head.y < 0 || head.y >= canvas.height
    ) {
        gameOver();
        return;
    }

    // Check collision with self
    if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
        gameOver();
        return;
    }

    snake.unshift(head);

    // Check if food is eaten
    // Move the food every FOOD_MOVE_INTERVAL snake moves
    foodMoveCounter++;
    if (foodMoveCounter >= FOOD_MOVE_INTERVAL) {
        moveFood();
        foodMoveCounter = 0;
    }

    if (head.x === food.x && head.y === food.y) {
        score++;
        document.getElementById('score').textContent = 'Score: ' + score;
        createExplosion(food.x, food.y);
        food = randomFood();
        bgColor = getRandomColor();
    } else {
        snake.pop();
    }
}

let bgColor = '#222';

// Explosion effect variables
let explosions = [];

function createExplosion(x, y) {
    const particles = [];
    for (let i = 0; i < 12; i++) {
        const angle = (Math.PI * 2 * i) / 12;
        const speed = 2 + Math.random() * 2;
        particles.push({
            x: x + box / 2,
            y: y + box / 2,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            alpha: 1,
            color: `hsl(${Math.floor(Math.random()*360)}, 90%, 60%)`
        });
    }
    explosions.push({ particles, life: 0 });
}

function drawExplosions() {
    for (let e = explosions.length - 1; e >= 0; e--) {
        const explosion = explosions[e];
        for (const p of explosion.particles) {
            ctx.globalAlpha = p.alpha;
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.globalAlpha = 1;
        }
        // Update particles
        for (const p of explosion.particles) {
            p.x += p.vx;
            p.y += p.vy;
            p.vx *= 0.92;
            p.vy *= 0.92;
            p.alpha *= 0.88;
        }
        explosion.life++;
        // Remove explosion after a few frames
        if (explosion.life > 18) {
            explosions.splice(e, 1);
        }
    }
}

function getRandomColor() {
    // Generate a random dark-ish color
    const r = Math.floor(32 + Math.random() * 128);
    const g = Math.floor(32 + Math.random() * 128);
    const b = Math.floor(32 + Math.random() * 128);
    return `rgb(${r},${g},${b})`;
}

function draw() {
    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawSnake();
    drawFood();
    drawExplosions();
}

function update() {
    moveSnake();
    draw();
}

function gameOver() {
    clearInterval(gameInterval);
    ctx.fillStyle = '#fff';
    ctx.font = '2rem monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Game Over', canvas.width / 2, canvas.height / 2);
    ctx.font = '1rem monospace';
    ctx.fillText('Refresh to play again', canvas.width / 2, canvas.height / 2 + 30);
}

document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft' && direction !== 'RIGHT') direction = 'LEFT';
    if (e.key === 'ArrowUp' && direction !== 'DOWN') direction = 'UP';
    if (e.key === 'ArrowRight' && direction !== 'LEFT') direction = 'RIGHT';
    if (e.key === 'ArrowDown' && direction !== 'UP') direction = 'DOWN';
    if (!gameInterval) {
        gameInterval = setInterval(update, 100);
    }
});

draw();
