<script>
    import { deviceParameters } from "../stores.js";
    import { deviceData } from "../stores.js";

    
    let selectedOperation;
    let chargeVLim = $deviceParameters.vmax;
    let dischargeVLim = $deviceParameters.vmin;
    let current = 1;
    let duration = 0;
    let waitDuration = 60;


    $: operations = $deviceData.operations;

    // $: chargeVPc = Math.round(100 * (chargeVLim - $deviceParameters.discharge_v) /
    //     ($deviceParameters.charge_v - $deviceParameters.discharge_v));
    // $: dischargeVPc = Math.round(100 * (dischargeVLim - $deviceParameters.discharge_v) /
    //     ($deviceParameters.charge_v - $deviceParameters.discharge_v));
    

    // $: voltageLimit = $deviceParameters.charge_v * voltRange/100;

    // $: if (voltRange) {
    //     const dv = $deviceParameters.charge_v - $deviceParameters.discharge_v;
    //     voltageLimit = $deviceParameters.discharge_v + dv * voltRange / 100;
    // }

    // function changeVLim() {
    //     const dv = $deviceParameters.charge_v - $deviceParameters.discharge_v;
    //     voltRange = 100 * (voltageLimit - $deviceParameters.discharge_v) / dv;
    //     console.log(voltageLimit);
    //     console.log(voltRange);
    // }

    $: if ($deviceParameters.vmax) {
        // chargeVLim = 0;
        // dischargeVLim = 0;
        handleVLim();
    }

    const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;

    async function handleSubmit() {
        console.log("submit");

        operations = [...operations, {operation: selectedOperation, params: {}}];

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
        
        console.log(responseData);
	}

    async function handleStart() {
        const response = await fetch(apiUrl + '/start-op', {method: "POST"});
    }

    async function handleStop() {
        const response = await fetch(apiUrl + '/stop-op', {method: "POST"});
    }

    async function handleClear() {
        operations = [];

        const response = await fetch(apiUrl + '/clear-op', {method: "POST"});
    }

    function getDescription(operation) {
        let desc = "";
        if (operation.operation === "charge") {
            desc = "Charge @" + operation.params.current + "A";
            desc += ", jusqu'à " + operation.params.vlim + "V";
        } else if (operation.operation === "discharge") {
            desc = "Décharge @" + operation.params.current + "A";
            desc += ", jusqu'à " + operation.params.vlim + "V";
        } else if (operation.operation === "wait") {
            desc = "Attendre " + operation.params.duration + "s";
        }

        if (duration in operation.params && operation.params.duration > 0) {
            desc += " pendant " + operation.params.duration + "s";
        }
        return desc;
    }

    function handleVLim() {
        console.log("chaning vlim");
        if (chargeVLim < $deviceParameters.vmin || chargeVLim > $deviceParameters.vmax) {
            chargeVLim = $deviceParameters.vmax;
        }
        if (dischargeVLim < $deviceParameters.vmin || dischargeVLim > $deviceParameters.vmax) {
            dischargeVLim = $deviceParameters.vmin;
        }
    }
</script>

<div id="container">

<div id="opForm">
    <div id="opSelector">
        <label for="operation" class="bold">Opération</label>

        <select name="operation" id="operation" bind:value={selectedOperation}>
            <option value="charge">Charge</option>
            <option value="discharge">Décharge</option>
            <option value="wait">Attendre</option>
        </select>
        <button id="addOperationButton" on:click={handleSubmit}>Ajouter</button>
    </div>

    <div>
        <!-- <fieldset> -->
        <p class="bold">Paramètres</p>
        <div id="parametersContainer">
            {#if selectedOperation === "charge" }
                <label for="current">Courant</label>
                <input type="number" id="current" name="current"
                    bind:value={current}
                    size="3" min="1" max="20"/> Amp<br><br>

                <label for="vlim">V lim</label>
                <input type="number" size="4" name="vlim" id="vlim"
                    min={$deviceParameters.vmin} max={$deviceParameters.vmax} step="0.1"
                    bind:value={chargeVLim} on:change={handleVLim}/> V
                <!-- <input type="range" id="taux" name="taux"
                    min={$deviceParameters.discharge_v} max={$deviceParameters.charge_v} step="0.01"
                    style="width: 100px; position: relative; bottom: -8px; margin: 0;"
                    bind:value={chargeVLim}>
                <span style="font-size: 0.8em;">{chargeVPc}%</span> -->
                <br><br>

                <label for="duration">Durée</label>
                <input type="number" id="duration" name="duration"
                    size="3" min="0" bind:value={duration} > sec
            {:else if selectedOperation === "discharge" }
                <label for="current">Courant</label>
                <input type="number" id="current" name="current"
                    bind:value={current}
                    size="3" min="1" max="20"/> Amp<br><br>

                <label for="vlim">V lim</label>
                <input type="number" size="4" name="vlim" id="vlim"
                    min={$deviceParameters.vmin} max={$deviceParameters.vmax} step="0.1"
                    bind:value={dischargeVLim}/> V
                <!-- <input type="range" id="taux" name="taux"
                    min={$deviceParameters.discharge_v} max={$deviceParameters.charge_v} step="0.01"
                    style="width: 100px; position: relative; bottom: -8px;"
                    bind:value={dischargeVLim}>
                <span style="font-size: 0.8em;">{dischargeVPc}%</span> -->
                <br><br>

                <label for="duration">Durée</label>
                <input type="number" id="duration" name="duration"
                    size="3" min="0" bind:value={duration} > sec
            {:else if  selectedOperation === "wait" }
                <label for="duration">Durée</label>
                <input type="number" id="duration" name="duration"
                    size="3" min="0" bind:value={waitDuration} > sec
            {/if}
        </div>
    <!-- </fieldset> -->
    </div>
</div>

<div id="rightContainer">
    <ul id="opList">
        {#each operations as op }
            <li class="listItem">
                {getDescription(op)}
                <input type="checkbox" style="position: absolute; right: 0px;"/>
            </li>
        {/each}
    </ul>

    <button class="progButton" on:click={handleStart}>Démarrer</button>
    <button class="progButton" on:click={handleStop} disabled>Stop</button>
    <button class="progButton" on:click={handleClear}>RAZ</button>

</div>
</div>


<style>
    #container {
        display: flex;
    }

    #opForm {
        width: 320px;
        height: 200px;
        background-color: gainsboro;
        float: left;
        position: relative;
    }

    .bold {
        font-weight: bold;
    }

    label {
        margin-right: 8px;
    }

    #opSelector {
        position: relative;
        /* left: 50px; */
    }

    #parametersContainer {
        margin-left: 24px;
    }

    #addOperationButton {
        position: absolute;
        /* bottom: 8px; */
        right: 0px;
        /* width: 80px; */
        /* height: 34px; */
        font-size: 1em;
        padding: 4px 6px 4px 6px;
    }

    #rightContainer {
        background-color: aquamarine;
        width: 300px;
    }

    #opList {
        overflow: auto;
        background-color: aqua;
        height: 126px;
        margin: 0px;
        padding: 20px;
        font-size: 0.9em;
    }

    .listItem {
        position: relative;
        font-size: 1.1em;
    }

    .progButton {
        font-size: 1em;
        /* height: 30px; */
        padding: 4px 6px 4px 6px;
    }
</style>