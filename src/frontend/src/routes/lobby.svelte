<script lang="ts">
    import { onDestroy } from 'svelte';
    import { room_store, socket } from '$lib/stores';

    import Centered from '$lib/Centered.svelte';

    var room;

    const unsubscribe = room_store.subscribe(value => {
        room = value;
    })

    $socket?.on("new_player", (username) => {
        room.players.push(username);
        room.players = room.players;
        room_store.set(room);
    })

    onDestroy(unsubscribe);
</script>

<Centered>
    {#if room != null && room != undefined}
        <h2>Waiting for more players...</h2>
        <div id="room-id">Room id: {room.roomId}</div>
        <div id="player-list">
            <h3>Players:</h3>
            {#each room.players as player}
                <div>{player.username}</div>
            {/each}
        </div>
        <a href="/play" class="button">Start</a>
    {:else}
        <div>Loading...</div>
    {/if}
</Centered>

<style>
    #room-id {
        font-weight: bold;
        margin-top: 2rem;
    }

    #player-list {
        margin: 1.9rem 0;
        margin-bottom: 1.5rem;
    }

    #player-list div {
        margin: 0.5rem 0;
    }

    .button {
        margin: auto;
    }
</style>