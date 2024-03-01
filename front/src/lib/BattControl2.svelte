<script>
    import { deviceData, deviceParameters, operationsChartDisplay } from "../stores.js";
    // import { deviceData } from "../stores.js";
    import { updateData } from "../stores.js";
    import { tooltip } from "../tooltip.js";

    
    let selectedOperation;
    let chargeVLim;
    let dischargeVLim;
    let current = $deviceParameters.charge_c;
    let duration = 0;       // In seconds
    let waitDuration = 60;  // In seconds

    // Update the list on component mount and whenever deviceState.operations changes
    // let operations = [];
    // $: {
    //     operations = $deviceData.operations || [];
    // }
    $: operations = $deviceData.operations;

    $: startDisabled = operations.length === 0 || $deviceData.device_mode != 0;
    $: stopDisabled = $deviceData.device_mode === 0;
    $: clearDisabled = $deviceData.operations.length === 0;

    const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;

    async function handleSubmit() {
        // Add a new operation to the list

        const opParams = {};
        if (selectedOperation === "charge") {
            opParams["current"] = current;
            opParams["vlim"] = chargeVLim;
            opParams["duration"] = duration;
        } else if (selectedOperation === "discharge") {
            opParams["current"] = current;
            opParams["vlim"] = dischargeVLim;
            opParams["duration"] = duration;
        } else if (selectedOperation === "wait") {
            opParams["duration"] = waitDuration;
        }

        const rpcData = {
            operation: selectedOperation,
            params: opParams,
        }

        const response = await fetch(apiUrl + '/add-op', {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(rpcData),
        });
        const responseData = await response.json();

        operationsChartDisplay.update((arr) => {
            arr.push(true);
            return arr;
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

    function getOpName(operation) {
        let desc = "";
        if (operation.type.startsWith("charge")) {
            desc = "Charge";
        } else if (operation.type.startsWith("discharge")) {
            desc = "Décharge";
        } else if (operation.type === "wait") {
            desc = "Attendre";
        }
        return desc;
    }

    function getOpParams(operation) {
        let desc = "";
        if (operation.type.startsWith("charge") || operation.type.startsWith("discharge")) {
            desc += operation.params.vlim + "V";
            desc += " @ " + operation.params.current + "A";
        } else if (operation.type === "wait") {
            desc += operation.params.duration + "s";
        }
        return desc;
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
    
    function handleChartToggle() {
        // operationsChartDisplay.set(checkedChart);
    }
</script>



<div id="container">

<div id="operation-form">
    <div id="operation-selector">
        <label for="operation" class="bold">Opération</label>

        <select name="operation" id="operation" bind:value={selectedOperation}>
            <option value="charge">Charge</option>
            <option value="discharge">Décharge</option>
            <option value="wait">Attendre</option>
        </select>
        <button id="addOperationButton" on:click={handleSubmit} title="Ajouter l'opération" use:tooltip><i class="fa-solid fa-right-to-bracket"></i></button>
    </div>

    <div>
        <!-- <fieldset> -->
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
                            size="4" min="0" bind:value={waitDuration}/></td>
                        <td>sec</td>
                    </tr>
                </table>
            {/if}
        </div>
    <!-- </fieldset> -->
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
                    <input type="checkbox" style="position: relative; right: 0px;" bind:checked={$operationsChartDisplay[index]} on:change={handleChartToggle} title="Afficher/masquer cette opération" use:tooltip/></td>
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
        <button class="prog-button" on:click={handleStart} disabled={startDisabled} title="Démarrer les opérations" use:tooltip><i class="fa-solid fa-play"></i></button>
        <button class="prog-button" disabled><i class="fa-solid fa-pause"></i></button>
        <button class="prog-button" on:click={handleStop} disabled={stopDisabled}><i class="fa-solid fa-stop"></i></button>
        <button class="prog-button" disabled><i class="fa-solid fa-floppy-disk"></i></button>
        <button class="red-prog-button" on:click={handleClear} disabled={clearDisabled} title="Effacer la liste des opérations" use:tooltip><i class="fa-solid fa-eraser"></i></button>
    </div>

</div>
</div>


<style>
    #container {
        display: flex;
        background-color: rgb(191, 238, 207);
        padding: 14px;
        border-radius: 30px;
    }

    #operation-form {
        width: 260px;
        height: 180px;
        padding: 16px;
        float: left;
        position: relative;
    }

    .bold {
        font-weight: bold;
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
        height: 140px;
        padding: 16px;
        border-radius: 20px;
        background-color: whitesmoke;
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
        justify-content: flex-end;
        gap: 4px;
        padding: 8px;
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