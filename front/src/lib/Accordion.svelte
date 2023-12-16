<script>
    import { slide } from 'svelte/transition';

    export let open = false;
    export let flex_size;
</script>


<div class="accordion" style="flex:{flex_size}">
    <div class:open class="header" on:mousedown={() => open=!open}>
        <h3 class="header-content"><slot name="head"></slot></h3>
    </div>
    
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
    
    .header {
        display:flex;
        height: 38px;
        align-items: center;
        /* justify-content: center; */
        padding-left: 16px;
        /* font-size: large; */
    }
    
    .open {
        background-color: #60c282;
    }

    .header:hover {
        font-weight: 720;
        background-color: #52c87b;
        padding-left: 32px;
        transition-duration: 200ms;
    }
    
    .header-content {
        /* flex: 1; */
        margin-right: 5px;
    }
    
    .details {
        /* background-color: rgb(176, 236, 197); */
        padding: 8px;
        padding-left: 26px;
    }

    @media print {
        .hide-on-print {
            display: none;
        }

        .accordion {
            border-radius: 50px;
            /* flex: 1; */
        }

        .open {
            background-color: rgb(176, 236, 197);
        }
    }
</style>