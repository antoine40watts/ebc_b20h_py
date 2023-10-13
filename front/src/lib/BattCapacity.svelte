<script>
    import { deviceParameters } from "../stores.js";

    const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;


    async function measureCapacity() {
        const url = apiUrl + "/measure";
        // const queryParams = `?cv=${charge_v}&cc=${charge_c}&dv=${discharge_v}&dc=${discharge_c}`;
        // console.log(url+queryParams);

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
        <p style="font-size: 20px">Capacité (Ah): </p>
    </div>

    <div class="container-capacity">
        <!-- <p>196,42</p>
        <p>194,96</p>
        <p>193,15</p> -->
        <button class="button-capacity" on:click={measureCapacity}>Mesurer</button>
    </div>

    <br>

    <div>
        <label for="cycles_input">Cycle(s)</label>
        <input type="number" id="cycles_input" name="cycles_input"
            size="3" value="1" min="1" max="6" />
    </div>
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
    .container-capacity {
        display: flex;
        justify-content: center;
        max-width: 400px;
        /* background-color: blueviolet; */
    }
    .container-capacity p {
        margin: 0 4px 0 4px;
        padding: 2px 4px 2px 4px;
        color: #50C74B;
        font-family: inherit;
        font-weight: 500;
        border: 1px solid #50C74B;
        border-radius: 12px;
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