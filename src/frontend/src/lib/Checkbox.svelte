<script>
    export let value = false;
</script>

<label class="container">
    <input type="checkbox" bind:checked={value}>
    <span class="checkmark"></span>
</label>

<style>
    .container input:checked ~ .checkmark {
        background-color: #EF894A;
    }

    .container {
        display: block;
        position: relative;
        cursor: pointer;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;

        width: 2rem;
        height: 2rem;
        background-color: white;
        border: 2px solid #EF894A;
        border-radius: 5px;
    }

    .container input {
        position: absolute;
        opacity: 0;
        cursor: pointer;
        height: 0;
        width: 0;
    }

    .checkmark {
        position: absolute;
        top: 50%;
        left: 50%;
        width: calc(2rem - 4px);
        height: calc(2rem - 4px);
        border-radius: 4px;
        transform: translate(-50%, -50%);
    }
</style>