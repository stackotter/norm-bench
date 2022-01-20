<script lang="ts">
    import Centered from '$lib/Centered.svelte';

    import { room_store } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { backendURL } from '$lib/env';

    var isLoading = false;
    var error = null;
    var username = "";
    var seed = "";

    const handleSubmit = () => {
        if (username == "") {
            error = "Please provide a username"
            return
        }

        isLoading = true;

        fetch(`${backendURL}/create_room?` + new URLSearchParams({
            'username': username,
            'seed': seed,
        })).then(async response => {
            if (response.status != 200) {
                error = await response.text();
                isLoading = false;
            } else {
                let json = await response.json();
                room_store.set(json);
                goto('/lobby');
            }
        })
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
    #error {
        margin-bottom: 0.75rem;
        margin-top: -0.75rem;
    }
</style>