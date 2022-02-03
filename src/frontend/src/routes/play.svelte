<script lang="ts">
    import Centered from '$lib/Centered.svelte';
    import { room_store, socket } from '$lib/stores';
    import { onDestroy } from 'svelte';

    import { Room, shuffleLetters, Word } from '$lib/room';
    import { startTimer } from '$lib/timer';
    import { Grid } from '$lib/grid';
    import { emitProgressUpdate } from '$lib/socket';

    // Game state

    var room: Room | null;
    var grid: Grid | null;

    var answersRevealed = false;
    var popupDismissed = false;

    // Timer

    var hasStartedTimer = false;
    var timeString = null;

    // Inputs

    var guess = "";

    // Handlers

    const unsubscribe = room_store.subscribe(value => {
        if (!room || room.roomId != value.roomId) {
            grid = new Grid(value);
            shuffleLetters();
            answersRevealed = false;
            popupDismissed = false;
            hasStartedTimer = false;
            timeString = null;
            guess = "";
        } else if (room.isCollaborative) {
            for (const word_index of room.placedWords) {
                const word = room.words[word_index];
                if (!grid.placedWords.includes(word.word)) {
                    grid.placeWord(word, false, false);
                }
            }
            grid = grid;
        }
        room = value;

        if (!hasStartedTimer && room.hasStarted) {
            hasStartedTimer = true;
            const timer = startTimer(time => {
                timeString = time;
                if (room.winner || answersRevealed) {
                    clearInterval(timer);
                }
            }, room.startTime);
        }
    });

    onDestroy(unsubscribe);

    const submitGuess = () => {
        if (grid.placedWords.includes(guess) || answersRevealed) {
            return
        }
        
        let normalizedGuess = guess.toLowerCase().trim();
        var word_index = 0;
        for (const word of room.words) {
            if (word.word == normalizedGuess) {
                // Place the word
                grid.placeWord(word, false, false);
                grid = grid;

                // Clear the guess input
                guess = "";
                
                // Notify other players of our progress
                emitProgressUpdate(word_index);
                
                // Check if we've won
                if (grid.placedWords.length == room.words.length) {
                    room_store.update(room => {
                        room.winner = room.username;
                        return room
                    })
                }

                if (room.seed == "norm") {
                    var extraWord: string | null = null;
                    if (word.word == "on" && grid.placedWords.includes("men") && !grid.placedWords.includes("no")) {
                        extraWord = "no";
                    } else if (word.word == "no" && grid.placedWords.includes("normalised") && !grid.placedWords.includes("on")) {
                        extraWord = "on";
                    } else if (word.word == "men" && grid.placedWords.includes("on") && !grid.placedWords.includes("no")) {
                        extraWord = "no";
                    } else if (word.word == "normalised" && grid.placedWords.includes("no") && !grid.placedWords.includes("on")) {
                        extraWord = "on";
                    }

                    if (extraWord) {
                        let word_index = room.words.findIndex(word => { return word.word == extraWord });
                        let word = room.words[word_index];

                        grid.placeWord(word, false, false);
                        grid = grid;

                        // Notify other players of our progress
                        emitProgressUpdate(word_index);
                    }
                }

                return
            }
            word_index += 1;
        }
    }

    const onKeyDown = (event) => {
        if (event.keyCode === 13) {
            event.preventDefault();
            submitGuess();
        }
    }

    const revealAnswers = () => {
        answersRevealed = true;
        room.words.forEach(word => {
            if (!grid.placedWords.includes(word.word)) {
                grid.placeWord(word, false, true);
            }
        });
        grid = grid;
    }

    const nextGame = () => {
        $socket?.emit("join_next_room", {
            "room_id": room.roomId,
            "username": room.username,
        });
    }

    $: room.winner && (() => {
        if (room.winner != room.username) {
            revealAnswers();
        }
    })()
</script>

<Centered>
    {#if room && grid}
        <div id="columns">
            <div class="column" id="game-column">
                <div id="grid">
                    {#each grid.rows as row}
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
                    {#each room.letters as letter}
                        <div class="square letter">{letter.toUpperCase()}</div>
                    {/each}
                    <div class="square letter" id="shuffle-button" on:click={shuffleLetters}>🔀</div>
                </div>
                <div id="form">
                    <input type="text" placeholder="Enter a word..." bind:value={guess} autofocus on:keydown={onKeyDown}>
                    <button class="button" on:click={submitGuess}>Go</button>
                </div>
            </div>

            <div class="column" id="leaderboard-column">
                <div id="timer">{timeString || "00:00.000"}</div>
                {#if !room.isCollaborative}
                    {#each room.players as player}
                        <div class="progress">
                            <div class="indicator" style="width: {player.progress / room.words.length * 100}%"/>
                            <div class="label">{player.username}</div>
                        </div>
                    {/each}
                {:else}
                    <div class="progress">
                        <div class="indicator" style="width: {room.placedWords.length / room.words.length * 100}%"/>
                        <div class="label">Team</div>
                    </div>
                {/if}

                <button class="button" id="give-up" on:click={(answersRevealed || room.winner) ? nextGame : revealAnswers}>
                    {(answersRevealed || room.winner) ? "Next" : "Give up"}
                </button>

                {#if answersRevealed || room.winner }
                    <div id="seed">Seed: {room.seed}</div>
                {/if}
            </div>
        </div>

        {#if room.winner && !popupDismissed}
            <div id="game-ended-popup" on:click={() => {popupDismissed = true}}>
                <div id="popup-text" on:click|stopPropagation={() => {return}}>
                    {room.isCollaborative ? "Go team!" : (room.winner == room.username ? "You win!" : `${room.winner} won!`)}
                    <button class="button" id="next-button" on:click={nextGame}>
                        Next
                    </button>
                    <div id="seed">Seed: {room.seed}</div>
                </div>
            </div>
        {/if}

        <div id="room-info">
            <div>Room id: {room.roomId}</div>
            <div>Letter count: {room.letterCount}</div>
            <div>Minimum word length: {room.minimumWordLength}</div>
            <div>Collaborative: {room.isCollaborative}</div>
        </div>
    {:else}
        <div>Loading...</div>
    {/if}
</Centered>

<style>
    #seed {
        margin-top: 1.5rem;
        font-size: 1rem;
    }

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
        margin-top: 1rem;
    }

    #next-button {
        width: 8rem;
        margin: auto;
        margin-top: 1rem;
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
    }

    #popup-text {
        padding: 4rem 7rem;
        background: white;
        font-size: 3rem;
        color: unset;
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
        margin-bottom: 1rem;
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