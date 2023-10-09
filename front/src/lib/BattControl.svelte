<script>

export let charge_v = 1;
export let charge_c = 1;
export let discharge_v = 1;
export let discharge_c = 1;

async function measureCapacity() {
    const url = "http://localhost:8000/measure";
    const queryParams = `?cv=${charge_v}&cc=${charge_c}&dv=${discharge_v}&dc=${discharge_c}`;
    console.log(url+queryParams);

    const rpc_data = {
        cv: charge_v,
        cc: charge_c,
        dv: discharge_v,
        dc: discharge_c,
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

        console.log(resultMessage)
}

</script>

<div class="container">
    <div style="text-align: center">
        <p style="font-size: 20px">Capacity (Ah): </p>
    </div>

    <div class="container-capacity">
        <!-- <p>196,42</p>
        <p>194,96</p>
        <p>193,15</p> -->
        <button class="button-capacity" on:click={measureCapacity}>Measure</button>
    </div>

    <br>

    <div style="text-align: center">
        <label for="cycles_input">Cycle(s)</label>
        <input type="text" id="cycles_input" name="cycles_input" size="1" value="1"/>
    </div>

    <div style="text-align: center">
            <label for="charge_input_v">Charge to</label>
            <input type="text" id="charge_input_v" name="charge_input_v" size="3"
                value={charge_v}/> V,
            <label for="charge_input_c">@</label>
            <input type="text" id="charge_input_c" name="charge_input_c" size="3"
                bind:value={charge_c}/> A
    </div>

    <div style="text-align: center">
            <label for="discharge_input_v">Discharge to</label>
            <input type="text" id="discharge_input_v" name="discharge_input_v" size="2" 
                value={discharge_v} /> V,
            <label for="discharge_input_c">@</label>
            <input type="text" id="discharge_input_c" name="discharge_input_c" size="2"
                bind:value={discharge_c} /> A
    </div>
</div>


<style>
    .container {
        /* background-color: blueviolet; */
        max-width: fit-content;
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
        border-radius: 10px;
        font-size: 1em;
    }

</style>