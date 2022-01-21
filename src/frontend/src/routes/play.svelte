<script lang="ts">
    import Centered from '$lib/Centered.svelte';
    import { room_store } from '$lib/stores';
    import { onDestroy } from 'svelte';

    import type { Word } from '$lib/room';
import { clear_loops } from 'svelte/internal';

    var room;

    var rows: string[][];
    var letters: string[];
    var placedWords: string[] = [];

    var guess = "";

    var won = false;

    var words: string[] = [];

    var clock = null;
    var timeString = "00:00.000";

    const shuffleLetters = () => {
        let currentIndex = letters.length, randomIndex;

        while (currentIndex != 0) {
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex--;

            [letters[currentIndex], letters[randomIndex]] = [
            letters[randomIndex], letters[currentIndex]];
        }

        // Make sure that we don't show them the 7 letter word.
        // TODO: optimise, at the moment it just checks every word (whereas it only needs to check the 7 letter words).
        let shownWord = letters.join();
        for (const word of room.words) {
            if (shownWord == word) {
                shuffleLetters()
                return
            }
        }

        letters = letters;
    }

    const setCell = (x: number, y: number, value: string) => {
        rows[y][x] = value;
    }

    const placeWord = (word: Word, asEmpty: boolean, gaveUp: boolean) => {
        if (!asEmpty) {
            placedWords.push(word.word);
            placedWords = placedWords;
        }

        for (var offset = 0; offset < word.word.length; offset++) {
            if (word.direction == "down") {
                var y = word.y + offset;
                if (gaveUp && rows[y][word.x] != " ") {
                    continue
                }
                setCell(word.x, y, asEmpty ? " " : (gaveUp ? `|${word.word[offset]}|` : word.word[offset]));
            } else {
                var x = word.x + offset;
                if (gaveUp && rows[word.y][x] != " ") {
                    continue
                }
                setCell(x, word.y, asEmpty ? " " : (gaveUp ? `|${word.word[offset]}|` : word.word[offset]));
            }
        }
    }

    const unsubscribe = room_store.subscribe(value => {
        room = value;

        if (room != null && room != undefined) {
            rows = [];
            for (var y = 0; y < room.height; y++) {
                var row = []
                for (var x = 0; x < room.width; x++) {
                    row.push('.'); // '.' means a square where no words go
                }
                rows.push(row);
            }

            room.words.forEach(word => {
                placeWord(word, true, false);
            });

            console.log(`${room.width}x${room.height}`);

            letters = room.letters;

            words = [];
            room.words.forEach(word => {
                words.push(word.word);
            });

            shuffleLetters();
        }
    })

    const submitGuess = () => {
        if (placedWords.includes(guess)) {
            return
        }

        for (const word of room.words) {
            if (word.word == guess) {
                placeWord(word, false, false);
                guess = "";

                if ((word == "on" && room.words.includes("no")) || (word == "no" && room.words.includes("on"))) {
                    placedWords.push(word == "on" ? "no" : "on")
                    placedWords = placedWords
                }

                if (words.includes("norm")) {
                    if (word.word == "on" && placedWords.includes("men") && !placedWords.includes("no")) {
                        placedWords.push("no");
                    } else if (word.word == "no" && placedWords.includes("normalised") && !placedWords.includes("on")) {
                        placedWords.push("on");
                    } else if (word.word == "men" && placedWords.includes("on") && !placedWords.includes("no")) {
                        placedWords.push("no");
                    } else if (word.word == "normalised" && placedWords.includes("no") && !placedWords.includes("on")) {
                        placedWords.push("on");
                    }
                }

                placedWords = placedWords

                if (placedWords.length == room.words.length) {
                    won = true;
                }

                return
            }
        }
    }

    const onKeyDown = (event) => {
        if (clock == null) {
            startTimer();
        }

        if (event.keyCode === 13) {
            event.preventDefault();
            submitGuess();
        }
    }

    const giveUp = () => {
        room.words.forEach(word => {
            if (!placedWords.includes(word)) {
                placeWord(word, false, true);
            }
        });
    }

    const startTimer = () => {
        clock = 0;
        let start = Date.now();
        var timer: NodeJS.Timer;
        timer = setInterval(() => {
            clock = Date.now() - start;

            var date = new Date(clock);

            var hours: string | number = date.getUTCHours();
            var minutes: string | number = date.getUTCMinutes();
            var seconds: string | number = date.getSeconds();
            var milliseconds: string | number = date.getMilliseconds();
            
            var string = "";
            
            if (hours > 0) {
                if (hours < 10) { hours = "0" + hours }
                string += hours + ":"
            }

            if (minutes < 10) { minutes = "0" + minutes }
            string += minutes + ":"

            if (seconds < 10) { seconds = "0" + seconds }
            string += seconds + "."

            if (milliseconds < 100) { milliseconds = "0" + milliseconds }
            if (milliseconds < 10) { milliseconds = "0" + milliseconds }
            if (milliseconds == 0) { milliseconds = "0" + milliseconds }
            string += milliseconds

            timeString = string;

            if (won) {
                clearInterval(timer);
            }
        }, 50);
    }

    onDestroy(unsubscribe);
</script>

<Centered>
    {#if room != null && room != undefined}
        <div id="room-info">
            <div>Room id: {room.roomId}</div>
            <div>Seed: {room.seed}</div>
        </div>
        <div id="columns">
            <div class="column" id="game-column">
                <div id="grid">
                    {#each rows as row}
                        <div class="row">
                            {#each row as cell}
                                {#if cell == "."}
                                    <div class="square background-square"></div>
                                {:else if cell == " "}
                                    <div class="square empty-square"></div>
                                {:else if cell.length == 3}
                                    <div class="square revealed">{cell.toUpperCase()[1]}</div>
                                {:else}
                                    <div class="square filled-square">{cell.toUpperCase()}</div>
                                {/if}
                            {/each}
                        </div>
                    {/each}
                </div>

                <div id="letters">
                    {#each letters as letter}
                        <div class="square letter">{letter.toUpperCase()}</div>
                    {/each}
                    <div class="square letter" id="shuffle-button" on:click={shuffleLetters}>🔀</div>
                </div>
                <div id="form">
                    <input type="text" placeholder="Enter a word..." bind:value={guess} autofocus on:keydown={onKeyDown}>
                    <button class="button" on:click={submitGuess}>Go</button>
                </div>

                {#if won}
                    <div id="game-ended-popup">
                        <div id="popup-text">You win!</div>
                    </div>
                {/if}
            </div>

            <div class="column" id="leaderboard-column">
                <div id="timer">{timeString}</div>
                <div class="progress">
                    <div class="indicator" style="width: {placedWords.length / room.words.length * 100}%"/>
                    <div class="label">{room.username}</div>
                </div>
                <button class="button" id="give-up" on:click={giveUp}>Give up</button>
            </div>
        </div>
    {:else}
        <div>Loading...</div>
    {/if}
</Centered>

<style>
    #timer {
        font-family: monospace;
        font-size: 1.5rem;
        margin-bottom: 2rem;
    }

    #shuffle-button {
        cursor: pointer;
    }

    #give-up {
        width: 8rem;
        margin-top: 2rem;
    }

    #columns {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        width: 100vw;
        height: 100vh;
    }

    .column {
        flex-basis: 0;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    #game-column {
        flex-grow: 3;
        position: relative;
    }

    #game-ended-popup {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #00000055;
        width: 100%;
        height: 100vh;

        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        animation: colorRotateBackground 4s linear 0s infinite;
    }

    @keyframes colorRotateBackground {
        from {
            background: #6666ff55;
        }
        10% {
            background: #0099ff55;
        }
        50% {
            background: #00ff0055;
        }
        75% {
            background: #ff339955;
        }
        100% {
            background: #6666ff55;
        }
    }

    #popup-text {
        padding: 4rem 7rem;
        background: white;
        font-size: 3rem;
        color: unset;

        animation: colorRotate 3s linear 0s infinite;
    }

    @keyframes colorRotate {
        from {
            color: #6666ff;
        }
        10% {
            color: #0099ff;
        }
        50% {
            color: #00ff00;
        }
        75% {
            color: #ff3399;
        }
        100% {
            color: #6666ff;
        }
    }

    #leaderboard-column {
        flex-grow: 1;
        height: calc(100% - 2rem);
        border-left: 2px solid #E18E57;
        justify-content: flex-start;
        padding-top: 2rem;
    }

    .progress {
        width: calc(100% - 6rem);
        background: #888888;
        color: white;
        text-align: left;
        position: relative;
        height: 3.5rem;
    }

    .indicator {
        background: #1a9fab;
        height: 100%;
        position: absolute;
        left: 0;
        top: 0;
        z-index: 0;
    }

    .label {
        z-index: 1000;
        position: absolute;
        top: 50%;
        left: 1rem;
        transform: translateY(-50%);
    }

    #grid {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 75%;
        height: 60vh;
        margin: 0;
        padding: 0;
    }

    .row {
        display: flex;
        flex-direction: row;
        flex-grow: 1;
        flex-shrink: 0;
        flex-basis: 0;
        width: 100%;
    }

    .square {
        flex-grow: 1;
        flex-shrink: 0;
        flex-basis: 0;
        background-color: #EF894A;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0.1rem;
    }

    .revealed {
        animation: fade-in-revealed 500ms;
        background-color: #924452;
        color: white;
    }

    @keyframes fade-in-revealed {
        from {
            background-color: #bbb;
            color: black;
        }

        to {
            background-color: #924452;
            color: white;
        }
    }

    .filled-square {
        animation: fade-in 500ms;
    }

    @keyframes fade-in {
        from {
            background-color: #bbb;
        }

        to {
            background-color: #EF894A;
        }
    }

    #letters {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        margin: auto;
        margin-top: 4rem;
        /* width: 29.5rem; */
    }

    .letter {
        background-color: #FAFAD6;
        width: 4rem;
        height: 4rem;
        flex-grow: none;
    }
    
    .empty-square {
        background-color: #bbb;
        color: #bbb;
    }

    .background-square {
        background-color: #00000000;
        color: #00000000;
    }

    #room-info {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        text-align: right;
    }

    #room-info div {
        margin-top: 0.5rem;
    }

    input, .button {
        margin: 0;
    }

    .button {
        width: 3rem;
        margin-left: 0.5rem;
    }

    #form {
        margin-top: 1rem;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
    }
</style>