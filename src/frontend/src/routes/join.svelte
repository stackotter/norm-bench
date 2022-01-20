<script lang="ts">
    import Centered from '$lib/Centered.svelte';
    import { room_store, Room } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { backendURL } from '$lib/env';

    var isLoading = false;
    var error = null;
    var roomId = null;
    var username = "";

    const handleSubmit = (event) => {
        if (username == "") {
            error = "Please provide a username"
            return
        }

        isLoading = true;

        fetch(`${backendURL}/join_room?` + new URLSearchParams({
            'room_id': roomId.toString(),
            'username': username,
        })).then(async response => {
            if (response.status != 200) {
                error = await response.text();
                isLoading = false;
            } else {
                let json = await response.json();
                let words = json["words"];
                let roomId = json["room_id"];
                let players = json["players"];
                let width = json["width"];
                let height = json["height"];
                let letters = json["letters"];
                let room: Room = {
                    username: username,
                    players: players,
                    roomId: roomId,
                    words: words,
                    width: width,
                    height: height,
                    letters: letters,
                };
                room_store.set(room);
                goto('/lobby');
            }
        })
    }
</script>

<Centered>
    {#if !isLoading}
        <h1>Join a room</h1>

        {#if error != null}
            <div id="error">{error}</div>
        {/if}

        <form on:submit|preventDefault={handleSubmit}>
            <input type="number" bind:value={roomId} placeholder="Room id">
            <input type="text" bind:value={username} placeholder="Username">
            <div class="button-group">
                <a href="/" class="button secondary-button">Cancel</a>
                <button class="button" type="submit">Join</button>
            </div>
        </form>
    {:else}
        <div>Loading...</div>
    {/if}
</Centered>

<style>
    #error {
        margin-bottom: 0.75rem;
        margin-top: -0.75rem;
    }
</style>