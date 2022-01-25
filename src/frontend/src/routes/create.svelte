<script lang="ts">
    import Centered from '$lib/Centered.svelte';
    import Checkbox from '$lib/Checkbox.svelte';
    import { socket } from '$lib/stores';

    // View state

    var isLoading = false;
    var error = null;

    // Inputs

    var username = "";
    var seed = "";
    var letterCount = 7;
    var minimumWordLength = 3;
    var isCollaborative = false;

    $: minimumWordLength = minimumWordLength >= letterCount ? letterCount - 1 : minimumWordLength

    // Handlers

    const handleSubmit = () => {
        if (username == "") {
            error = "Please provide a username"
            return
        }

        isLoading = true;

        $socket?.on("error", (message) => {
            error = message;
            isLoading = false;
        });

        $socket?.emit("create_room", {
            'username': username,
            'seed': seed,
            'letter_count': letterCount,
            'minimum_word_length': minimumWordLength,
            'is_collaborative': isCollaborative,
        });
    }
</script>

<Centered>
    {#if !isLoading}
        <h1>Create a new room</h1>

        {#if error != null}
            <div id="error">{error}</div>
        {/if}

        <form on:submit|preventDefault={handleSubmit}>
            <input type="text" bind:value={username} placeholder="Username">
            <input type="text" bind:value={seed} placeholder="Seed (optional)">
            <div class="label">Letter count: {letterCount}</div>
            <input type="range" min="4" max="20" bind:value={letterCount} class="slider">
            <div class="label">Minimum word length: {minimumWordLength}</div>
            <input type="range" min="3" max={letterCount <= 14 ? letterCount - 1 : 14} bind:value={minimumWordLength} class="slider">
            <div class="row">
                <div class="label">Collaboration:</div>
                <Checkbox bind:value={isCollaborative}/>
            </div>
            <div class="button-group">
                <a href="/" class="button secondary-button">Cancel</a>
                <button class="button" type="submit">Create</button>
            </div>
        </form>
    {:else}
        <div>Loading...</div>
    {/if}
</Centered>

<style>
    .row {
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    .label {
        margin-right: 0.5rem;
    }

    #error {
        margin-bottom: 0.75rem;
        margin-top: -0.75rem;
    }

    form {
        width: calc(18.5rem + 4px);
        margin: auto;
        text-align: left;
    }

    .button-group {
        margin-top: 0.8rem;
    }

    .button-group .button:first-child {
        margin-left: 0;
    }

    .button-group .button:last-child {
        margin-right: 0;
    }

    .label {
        font-size: 1.1rem;
        margin-top: 1.8rem;
        margin-bottom: 1.8rem;
    }
</style>