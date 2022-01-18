<script>
    import Centered from "$lib/Centered.svelte";

    const quotes = [
        "Loops! - Norm, 2022",
        "GG - Norm, 2022",
        "Why is that not in there! - Everyone, n.d.",
        "Sloth should've definitely been in there :( - Cameron, 2022",
        "Sean and Norm are starting to question your wordbench skills - The staff, 2022",
        "pro, but not con??"
    ]

    const quote = quotes[Math.floor(Math.random() * quotes.length)]
</script>

<Centered>
    <h1>Welcome to NormBench</h1>

    <div id="buttons">
        <a class="button" href="/create">Create room</a>
        <a class="button" href="/join">Join room</a>
    </div>

    <p id="quote">{quote}</p>
</Centered>

<style>
    #buttons {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        margin: 2rem 0;
    }

    #quote {
        margin-top: 2rem;
        font-size: 0.9rem;
    }

    .button {
		margin: 0 0.5rem;
    }
</style>