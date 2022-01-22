<script lang="ts">
    import Centered from '$lib/Centered.svelte';

    import { room_store, socket } from '$lib/stores';
    import { goto } from '$app/navigation';

    var isLoading = false;
    var error = null;
    var roomId = null;
    var username = "";

    const handleSubmit = () => {
        if (username == "") {
            error = "Please provide a username"
            return
        }

        isLoading = true;

        $socket?.on("joined_room", (json) => {
            json["username"] = username;
            room_store.set(json);
            goto('/lobby');
        });

        $socket?.on("error", (message) => {
            error = message;
            isLoading = false;
        });

        $socket?.emit("join_room", {
            'username': username,
            'room_id': roomId,
        });
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