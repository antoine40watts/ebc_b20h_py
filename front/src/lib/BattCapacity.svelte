<script>
    import { deviceParameters } from "../stores.js";
    import { batteryData } from "../stores.js";

    const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;


    async function measureCapacity() {
        const url = apiUrl + "/measure";

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

        console.log(rpc_data);
        console.log(resultMessage);
    }
</script>

<div class="container">
    <div>
        <p style="font-size: 1.5rem">Capacité</p>
    </div>
    
    <div style="text-align: left;">
        <span>Originale: </span>
        <span style="font-weight: bold;">{$deviceParameters.original_capacity / 1000} Ah</span>
        <p>Réelle:
            {#if $batteryData.capacity > 0}
                <span class="capacity-result">{$batteryData.capacity / 1000} Ah</span>
            {/if}
            <button class="button-capacity" on:click={measureCapacity}>Mesurer</button>
        </p>
    </div>

    <!-- <div>
        <label for="cycles_input">Cycle(s)</label>
        <input type="number" id="cycles_input" name="cycles_input"
            size="3" value="1" min="1" max="6" />
    </div> -->
</div>


<style>
    .container {
        /* background-color: blueviolet; */
        /* max-width: fit-content; */
        text-align: center;
    }
    .container div {
        margin: 6px;
    }
    .capacity-result {
        color: #50C74B;
        font-size: 1.2em;
        font-weight: 600;
    }
    
    .button-capacity {
        margin: 0 4px 0 4px;
        padding: 4px;
        border-radius: 16px;
        font-size: 1rem;
    }

    @media print{
        .button-capacity {
            display: none;
        }
        .container {
            position: absolute;
            bottom: 40px;
        }
    }
</style>