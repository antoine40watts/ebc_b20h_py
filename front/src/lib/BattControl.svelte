<script>
    import { deviceParameters } from "../stores.js";

    const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;


    async function sendDevice(command) {
        const url = apiUrl + "/" + command;

        const rpc_data = {
            cv: $deviceParameters.charge_v,
            cc: $deviceParameters.charge_c,
            dv: $deviceParameters.discharge_v,
            dc: $deviceParameters.discharge_c,
        };
        
        let resultMessage = '';

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(rpc_data),
            });
        
            if (!response.ok) {
                throw new Error('RPC request failed');
            }
            
            const data = await response.json();
            resultMessage = data.message;
        } catch (error) {
            console.error('Error making RPC call:', error);
            resultMessage = 'RPC call failed';
        }
    }
</script>


<div class="container">
    <div style="text-align: center">
            <label for="charge_input_v">Charge to</label>
            <input type="number" id="charge_input_v" name="charge_input_v" size="4"
                bind:value={$deviceParameters.charge_v}/> V,
            <label for="charge_input_c">@</label>
            <input type="number" id="charge_input_c" name="charge_input_c" size="2"
                bind:value={$deviceParameters.charge_c}/> A
            <div><button class="button-charge" on:click={() => sendDevice("charge")}>Charge</button></div>
    </div>

    <div style="text-align: center">
            <label for="discharge_input_v">Discharge to</label>
            <input type="number" id="discharge_input_v" name="discharge_input_v" size="4" 
                bind:value={$deviceParameters.discharge_v} /> V,
            <label for="discharge_input_c">@</label>
            <input type="number" id="discharge_input_c" name="discharge_input_c" size="2"
                bind:value={$deviceParameters.discharge_c} /> A
            <div><button class="button-discharge" on:click={() => sendDevice("discharge")}>Discharge</button></div>
    </div>
</div>


<style>
    .container {
        /* background-color: blueviolet; */
        text-align: center;
    }

    button {
        margin: 8px;
    }
</style>