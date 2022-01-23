<script lang="ts">
    import { room_store, socket } from '$lib/stores';

    import Centered from '$lib/Centered.svelte';
    import { goto } from '$app/navigation';

    var room = $room_store

    const play = () => {
        room_store.update(room => {
            room.hasStarted = true;
            return room
        });

        $socket?.emit("start_game", {
            "room_id": room.roomId
        });

        goto("/play");
    }
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
        <button class="button" on:click={play}>Start</button>
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