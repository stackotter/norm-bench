<div id="centerer">
    <div id="content">
        <slot></slot>
    </div>
</div>

<style>
    #centerer {
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    #content {
        text-align: center;
    }
</style>