<script>

    export let showModal;

    let dialog; // HTMLDialogElement

	$: if (dialog && showModal) dialog.showModal();
</script>


<dialog bind:this={dialog}>
    <p class="error-message">Appareil hors-ligne</p>
</dialog>


<style>
    dialog {
        border-radius: 24px;
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