<script lang="ts">
    import Centered from '$lib/Centered.svelte';
    import { room_store, Word } from '$lib/stores';
    import { onDestroy } from 'svelte';

    var room;

    var rows: string[][];
    var letters: string[];

    var guess = "";

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
    }

    const setCell = (x: number, y: number, value: string) => {
        rows[y][x] = value;
    }

    const placeWord = (word: Word, asEmpty: boolean) => {
        console.log(`${word.word}, x ${word.x}, y ${word.y}`)
        for (var offset = 0; offset < word.word.length; offset++) {
            if (word.direction == "down") {
                var y = word.y + offset;
                setCell(word.x, y, asEmpty ? " " : word.word[offset]);
            } else {
                var x = word.x + offset;
                setCell(x, word.y, asEmpty ? " " : word.word[offset]);
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
                placeWord(word, true);
            });

            letters = room.letters;

            shuffleLetters();
        }
    })

    const submitGuess = () => {
        console.log("submit")
        for (const word of room.words) {
            if (word.word == guess) {
                placeWord(word, false);
                guess = "";
            }
        }
    }

    const onKeyDown = (event) => {
        if (event.keyCode === 13) {
            event.preventDefault();
            submitGuess();
        }
    }

    onDestroy(unsubscribe);
</script>

<Centered>
    {#if room != null && room != undefined}
        <div id="room-id">Room id: {room.roomId}</div>
        <div id="grid">
            {#each rows as row}
                <div class="row">
                    {#each row as cell}
                        {#if cell == "."}
                            <div class="square background-square"/>
                        {:else if cell == " "}
                            <div class="square empty-square"/>
                        {:else}
                            <div class="square">{cell.toUpperCase()}</div>
                        {/if}
                    {/each}
                </div>
            {/each}
        </div>
        <div id="letters">
            {#each letters as letter}
                <div class="square letter">{letter.toUpperCase()}</div>
            {/each}
        </div>
        <div id="form">
            <input type="text" placeholder="Enter a word..." bind:value={guess} autofocus on:keydown={onKeyDown}>
            <button class="button">Go</button>
        </div>
    {:else}
        <div>Loading...</div>
    {/if}
</Centered>

<style>
    .square {
        width: 4rem;
        height: 4rem;
        background-color: #EF894A;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0.1rem;
    }

    #letters {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        margin-top: 4rem;
    }

    .letter {
        background-color: #FAFAD6;
    }
    
    .empty-square {
        background-color: #bbb;
    }

    .background-square {
        background-color: #00000000;
    }

    .row {
        display: flex;
        flex-direction: row;
    }

    #room-id {
        font-weight: bold;
        position: fixed;
        top: 1rem;
        right: 1rem;
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