<script>
    import { makeRPCRequest } from "../main.js";
    import { apiUrl, updateData } from "../stores.js";
    import { deviceData, deviceParameters, operationsChartDisplay } from "../stores.js";
    import { tooltip } from "../tooltip.js";

    
    let selectedOperation;
    let chargeVLim;
    let dischargeVLim;
    let current = $deviceParameters.charge_c;
    let duration = 0;       // In seconds
    let waitDuration = 60;  // In seconds
    

    $: operations = $deviceData.operations;

    $: startDisabled = operations.length === 0 || $deviceData.device_mode != 0;
    $: stopDisabled = $deviceData.battery_state === 0 && $deviceData.device_mode === 0;
    $: clearDisabled = $deviceData.operations.length === 0;
    $: saveDisabled = $deviceData.operations.length === 0;


    
    function getOpName(operation) {
        let desc = "";
        if (operation.type.startsWith("charge")) {
            desc = "Charge";
        } else if (operation.type.startsWith("discharge")) {
            desc = "Décharge";
        } else if (operation.type === "wait") {
            desc = "Attendre";
        } else if (operation.type === "adjust") {
            desc = "Adjust";
        }
        return desc;
    }

    function getOpParams(operation) {
        let desc = "";
        if (operation.type.startsWith("charge")
            || operation.type.startsWith("discharge")
            || operation.type.startsWith("adjust")) {
            desc += operation.params.vlim + "V";
            desc += " @ " + operation.params.current + "A ";
        }
        if (operation.params.duration > 0) {
            desc += operation.params.duration + "s";
        }
        return desc;
    }

    async function handleAddOp() {
        // Add a new operation to the program list

        let operations = [];

        if (selectedProgram) {
            operations = selectedProgram;
        } else {
            const operation = {type: selectedOperation};
            const params = {};

            if (selectedOperation === "charge") {
                params["current"] = current;
                params["vlim"] = chargeVLim;
                params["duration"] = duration;
            } else if (selectedOperation === "discharge") {
                params["current"] = current;
                params["vlim"] = dischargeVLim;
                params["duration"] = duration;
            } else if (selectedOperation === "wait") {
                params["duration"] = waitDuration;
            } else if (selectedOperation === "adjust") {
                params["current"] = current;
                params["vlim"] = dischargeVLim;
                params["duration"] = duration;
            }
            operation.params = params;

            operations.push(operation)
        }

        const response = await makeRPCRequest("add_operations", operations);

        operationsChartDisplay.update((arr) => {
            return [...arr, ...Array(operations.length).fill(true)];
        });

        await updateData();
	}

    async function handleStart() {
        const response = await fetch(apiUrl + '/start-ops', {method: "POST"});
        await updateData();
    }

    async function handleStop() {
        const response = await fetch(apiUrl + '/stop-ops', {method: "POST"});
        await updateData();
    }

    async function handleClear() {
        const response = await fetch(apiUrl + '/clear-ops', {method: "POST"});
        await updateData();
        operationsChartDisplay.set([]);
    }

    async function handleDeleteOp(index) {
        const params = `?idx=${index}`
        const response = await fetch(apiUrl + '/delete-op' + params, {method: "POST"});
        await updateData();
        operationsChartDisplay.update((array) => {
            array.splice(index, 1);
            return array
        });
    }

    function handleVLim() {
        chargeVLim = Math.min(Math.max(chargeVLim, $deviceParameters.discharge_v), $deviceParameters.charge_v);
        dischargeVLim = Math.min(Math.max(dischargeVLim, $deviceParameters.discharge_v), $deviceParameters.charge_v);
    }

    // Update the charge/discharge vlim parameters when changing battery nominal voltage
    const unsubscribe = deviceParameters.subscribe((value) => {
        chargeVLim = value.charge_v;
        dischargeVLim = value.discharge_v;
    });
    


    // Stored programs

    let programNameDialog;
    let showProgramNameModal = false;
    let programNameValue = "";
    $: if (programNameDialog && showProgramNameModal) programNameDialog.showModal();
    
    function handleSaveButton() {
        // Save list of operations
        // Show a modal asking for a name for the program
        programNameValue = "";
        showProgramNameModal = true;
    }

    async function handleDeleteProgram() {
        const response = await makeRPCRequest("delete_program", {name: selectedOperation});
        getPrograms();
    }


    let storedPrograms = null;
    
    async function getPrograms() {
        storedPrograms = await makeRPCRequest("get_program_names", {});
    }
    
    async function saveProgram() {
        if (programNameValue === "") {
            return;
        }
        if (["charge", "discharge", "adjust", "wait"].includes(programNameValue)) {
            return;
        }
        const response = await makeRPCRequest("save_program", {name: programNameValue});
        await getPrograms();
        selectedOperation = programNameValue;

    }
    
    let selectedProgram = null;
    $: {
        if (storedPrograms && selectedOperation && storedPrograms.includes(selectedOperation)) {
            makeRPCRequest("get_program", {name: selectedOperation}).then(
                value => selectedProgram = value
            );
        } else {
            selectedProgram = null;
        }
    }
    
    getPrograms();
</script>



<div id="container">

    <div id="operation-form">
        <div id="operation-selector">
            <label for="operation" class="bold">Opération</label>

            <select name="operation" id="operation" bind:value={selectedOperation}>
                {#if storedPrograms && storedPrograms.length > 0}
                    {#each storedPrograms as prog, index}
                        <option>{prog}</option>
                    {/each} 
                    <hr>
                {/if}
                <option value="charge">Charge</option>
                <option value="discharge">Décharge</option>
                <option value="wait">Attendre</option>
                <option value="adjust">Adjust</option>
            </select>
            <button id="addOperationButton" on:click={handleAddOp} title="Ajouter l'opération" use:tooltip><i class="fa-solid fa-right-to-bracket"></i></button>
        </div>

        <div>
            {#if storedPrograms && storedPrograms.includes(selectedOperation)}
                <p class="bold">Contenu</p>
                {#if selectedProgram}
                    <div id="program-list">
                    <ol style="margin: 0">
                    {#each selectedProgram as op, index}
                        <li>{getOpName(op)} {getOpParams(op)}</li>
                    {/each}
                    </ol>
                    </div>
                {/if}
                <button class="prog-button" style="position: absolute; bottom: 0; right: 16px;" on:click={handleDeleteProgram} title="Supprimer le programme" use:tooltip>
                    <i class="fa-regular fa-trash-can"></i>
                </button>
            {:else}
                <p class="bold">Paramètres</p>
                <div id="parametersContainer">
                    {#if selectedOperation === "charge" }
                        <table class="params-table">
                            <tr>
                                <td class="param-name-col"><label for="current">Courant</label></td>
                                <td class="input-col"><input type="number" id="current" name="current"
                                    bind:value={current}
                                    size="4" min="1" max="20"/></td>
                                <td>Amp</td>
                            </tr>
                            <tr>
                                <td class="param-name-col"><label for="vlim">V lim</label></td>
                                <td class="input-col"><input type="number" size="4" name="vlim" id="vlim"
                                    min={$deviceParameters.discharge_v} max={$deviceParameters.charge_v} step="0.1"
                                    bind:value={chargeVLim} on:change={handleVLim}/></td>
                                <td>V</td>
                            </tr>
                            <tr>
                                <td class="param-name-col"><label for="duration">Durée</label></td>
                                <td class="input-col"><input type="number" id="duration" name="duration"
                                    size="4" min="0" bind:value={duration}/></td>
                                <td>sec</td>
                            </tr>
                        </table>
                        <!-- <input type="range" id="taux" name="taux"
                            min={$deviceParameters.discharge_v} max={$deviceParameters.charge_v} step="0.01"
                            style="width: 100px; position: relative; bottom: -8px; margin: 0;"
                            bind:value={chargeVLim}>
                        <span style="font-size: 0.8em;">{chargeVPc}%</span> -->
                    {:else if selectedOperation === "discharge" }
                        <table class="params-table">
                            <tr>
                                <td class="param-name-col"><label for="current">Courant</label></td>
                                <td class="input-col"><input type="number" id="current" name="current"
                                    bind:value={current}
                                    size="4" min="1" max="20"/></td>
                                <td>Amp</td>
                            </tr>
                            <tr>
                                <td class="param-name-col"><label for="vlim">V lim</label></td>
                                <td class="input-col"><input type="number" size="4" name="vlim" id="vlim"
                                    min={$deviceParameters.discharge_v} max={$deviceParameters.charge_v} step="0.1"
                                    bind:value={dischargeVLim} on:change={handleVLim}/></td>
                                <td>V</td>
                            </tr>
                            <tr>
                                <td class="param-name-col"><label for="duration">Durée</label></td>
                                <td class="input-col"><input type="number" id="duration" name="duration"
                                    size="4" min="0" bind:value={duration}/></td>
                                <td>sec</td>
                            </tr>
                        </table>
                        <!-- <input type="range" id="taux" name="taux"
                            min={$deviceParameters.discharge_v} max={$deviceParameters.charge_v} step="0.01"
                            style="width: 100px; position: relative; bottom: -8px;"
                            bind:value={dischargeVLim}>
                        <span style="font-size: 0.8em;">{dischargeVPc}%</span> -->
                    {:else if  selectedOperation === "wait" }
                        <table class="params-table">
                            <tr>
                                <td class="param-name-col"><label for="duration">Durée</label></td>
                                <td class="input-col"><input type="number" id="duration" name="duration"
                                    size="4" min="1" bind:value={waitDuration}/></td>
                                <td>sec</td>
                            </tr>
                        </table>
                    {:else if selectedOperation === "adjust" }
                        <table class="params-table">
                            <tr>
                                <td class="param-name-col"><label for="current">Courant</label></td>
                                <td class="input-col"><input type="number" id="current" name="current"
                                    bind:value={current}
                                    size="4" min="1" max="20"/></td>
                                <td>Amp</td>
                            </tr>
                            <tr>
                                <td class="param-name-col"><label for="vlim">V lim</label></td>
                                <td class="input-col"><input type="number" size="4" name="vlim" id="vlim"
                                    min={$deviceParameters.discharge_v} max={$deviceParameters.charge_v} step="0.1"
                                    bind:value={dischargeVLim} on:change={handleVLim}/></td>
                                <td>V</td>
                            </tr>
                            <tr>
                                <td class="param-name-col"><label for="duration">Durée</label></td>
                                <td class="input-col"><input type="number" id="duration" name="duration"
                                    size="4" min="0" bind:value={duration}/></td>
                                <td>sec</td>
                            </tr>
                        </table>
                    {/if}
                </div>
            {/if}

        </div>
    </div>

    <div id="right-container">
        <div id="operations-list">
            <table >
                {#each operations as op, index}
                <tr>
                    {#if op.status === 1}
                    <td class="op-status-icon"><i class="fa-solid fa-spinner fa-pulse"></i></td>
                    {:else if op.status === 2}
                    <td class="op-status-icon"><i class="fa-solid fa-check"></i></td>
                    {:else}
                    <td class="op-status-icon"></td>
                    {/if}

                    <td class="op-name">{getOpName(op)}</td>
                    <td class="op-params">{getOpParams(op)}</td>
                    <td class="op-chart">
                        <input type="checkbox" style="position: relative; right: 0px;" bind:checked={$operationsChartDisplay[index]} title="Afficher/masquer cette opération" use:tooltip/></td>
                    {#if op.status === 0}
                    <td class="op-delete"><button class="delete-op-button" on:click={() => {handleDeleteOp(index)}} title="Effacer cette opération" use:tooltip><i class="fa-solid fa-delete-left"></i></button></td>
                    {:else}
                    <td class="op-delete"></td>
                    {/if}
                </tr>
                {/each}
            </table>
        </div>

        <div id="button-bar">
            <button class="prog-button" on:click={handleStart} disabled={startDisabled} title="Démarrer le programme" use:tooltip><i class="fa-solid fa-play"></i></button>
            <!-- <button class="prog-button" disabled><i class="fa-solid fa-pause"></i></button> -->
            <button class="prog-button" on:click={handleStop} disabled={stopDisabled}><i class="fa-solid fa-stop"></i></button>
            <button class="prog-button" on:click={handleSaveButton} disabled={saveDisabled} title="Enregistrer le programme" use:tooltip><i class="fa-solid fa-floppy-disk"></i></button>
            <button class="red-prog-button" on:click={handleClear} disabled={clearDisabled} title="Effacer la liste des opérations" use:tooltip><i class="fa-solid fa-eraser"></i></button>
        </div>

    </div>

</div>


<!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
<dialog
	bind:this={programNameDialog}
	on:close={() => (showProgramNameModal = false)}
	on:click|self={() => programNameDialog.close()}
>
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div on:click|stopPropagation>
		<h2>Veuillez choisir un nom</h2>
		
        <input type="text" id="client-name" name="client-name"
                    bind:value={programNameValue}
                    required minlength="1" maxlength="32" size="24"/>
        
		<!-- svelte-ignore a11y-autofocus -->
        <div id="button-bar">
            <button autofocus on:click={() => {programNameDialog.close(); saveProgram()}}>Valider</button>
            <button on:click={() => programNameDialog.close()}>Annuler</button>
        </div>
	</div>
</dialog>



<style>
    #container {
        display: flex;
        background-color: rgb(191, 238, 207);
        padding: 14px;
        border-radius: 24px 24px 0 0;
    }

    #operation-form {
        width: 280px;
        height: 180px;
        padding: 16px;
        /* float: left;
        position: relative; */
    }

    dialog {
		max-width: 32em;
		border-radius: 0.5em;
		border: none;
		padding: 16px;
	}

    .bold {
        font-weight: bold;
    }

    input {
        background-color: transparent;
        border: none;
        border-bottom: 1px solid #0f471a;
        font-size: 1em;
        font-weight: 500;
        text-align: center;
    }

    input:hover {
        border-bottom: 1px solid #50C74B;
    }

    input:focus {
        outline: none;
        border: none;
        border-bottom: 2px solid #50C74B;
    }

    label {
        margin-right: 8px;
    }

    #operation-selector {
        position: relative;
    }

    #parametersContainer {
        margin-left: 24px;
    }

    .params-table tr {
        height: 32px;
    }

    .params-table .param-name-col {
        width: 80px;
    }

    .params-table .input-col {
        width: 70px;
    }

    #addOperationButton {
        position: absolute;
        right: 0px;
        padding: 4px 6px 4px 6px;
        font-size: 1em;
    }

    #right-container {
        width: 290px;
    }

    #operations-list {
        height: 156px;
        padding: 8px;
        border-radius: 16px;
        background-color: whitesmoke;
        overflow: auto;
        font-size: 0.9em;
    }

    #program-list {
        position: relative;
        top: -8px;
        height: 100px;
        overflow: auto;
        font-size: 0.9em;
    }

    table .op-status-icon {
        width: 20px;
    }

    table .op-name {
        width: 80px;
        font-weight: 600;
    }

    table .op-params {
        width: 100px;
    }

    table .op-chart {
        width: 26px;
    }

    table .op-delete {
        width: 28px;
    }

    #button-bar {
        display: flex;
        justify-content: center;
        gap: 4px;
        padding-top: 8px;
    }

    .delete-op-button {
        color: #A00;
        background-color: transparent;
        border: none;
    }
    .delete-op-button:hover {
        color: #E00;
    }

    .prog-button {
        font-size: 1em;
        border-radius: 8px;
        padding: 4px 6px 4px 6px;
    }

    .red-prog-button {
        color: #A00;
        font-size: 1em;
        border-radius: 8px;
        padding: 4px 6px 4px 6px;
    }

    .red-prog-button:disabled {
        color: rgb(160, 128, 128);
    }
</style>