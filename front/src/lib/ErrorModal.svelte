<script>
    import { deviceData } from "../stores.js";

    let dialog; // HTMLDialogElement
    
	$: if (dialog && $deviceData.device_error) dialog.showModal();
    $: if (dialog && dialog.open && !$deviceData.device_error) dialog.close();
</script>


<dialog bind:this={dialog}>
    <p class="error-message">Appareil hors-ligne</p>
</dialog>


<style>
    dialog {
        border-radius: 24px;
        padding: 0 30px 0 30px;
    }
    dialog::backdrop {
        backdrop-filter: blur(4px);
    }

    .error-message {
        color: red;
        font-size: 2em;
        font-weight: bold;
    }
</style>