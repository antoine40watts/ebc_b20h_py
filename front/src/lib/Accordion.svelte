<script>
    import { slide } from 'svelte/transition';

    export let open = false;
    export let flex_size;
</script>


<div class="accordion" style="flex:{flex_size}">
    <div class:open class="header" on:mousedown={() => open=!open}>
        <span class="header-icon" style="margin-right: 10px">
            <slot name="header-icon"></slot>
        </span>
        <h3>
            <span class="header-title">
                <slot name="header-title"></slot>
            </span>
        </h3>
    </div>
    <span class="header-search">
        <slot name="header-search"></slot>
    </span>
    
    {#if open}
    <div class="details" transition:slide={{ duration: 200 }}>
        <slot name="details"></slot>
    </div>
    {/if}
</div>
  

<style>
    .accordion {
        margin: 0;
        background-color: rgb(191, 238, 207);
        flex-grow: 1;
    }
    
    .open {
        background-color: #6fdd96;
    }
    
    .header {
        display:flex;
        height: 38px;
        align-items: center;
        color: #57976d;
        /* color: #0006; */
    }

    .header-icon {
        margin-left: 16px;
        font-size: 1.2em;
    }

    .header-title {
        margin-left: 8px;
    }

    .header-search {
        position: absolute;
        margin: 4px;
        top: 0;
        right: 4px;
        /* height: 1em; */
    }
    
    .header:hover {
        background-color: #6fdd96;
        color: #2a4935;
        transition-duration: 200ms;
    }

    .header:hover .header-title {
        margin-left: 16px;
        transition-duration: 200ms;
    }

    .header:hover .header-icon {
        font-size: 1.7em;
        margin-left: 14px;
        transition-duration: 200ms;
    }
    
    .details {
        padding: 12px;
    }

    @media print {
        .accordion {
            border-radius: 50px;
        }

        .open {
            background-color: rgb(176, 236, 197);
        }

        .details {
            padding-top: 2px;
        }
    }
</style>