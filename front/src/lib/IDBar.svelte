<script>
    import { deviceParameters } from "../stores.js";

    let cell_tech_list = [
        "Li-ion",
        "Li-Fe",
        "NiMH",
        "Lead Acid",
        "other",
    ]

    let cells_s = 1;
    let cells_p = 1;
    let cell_cap = 3200;
    let cell_tech = cell_tech_list[0];

    function updateParams() {
        deviceParameters.update((params) => {
            params.charge_v = Math.round(4.2 * cells_s * 100) / 100;
            params.discharge_v = Math.round(2.7 * cells_s * 100) / 100;
            params.original_capacity = Math.round(cell_cap * cells_s * cells_p);
            return params;
        });
    }

</script>

<div class="container">


    <div class="input-group">
        <span>
            <label for="client_id">Client #</label>
            <input type="text" id="client_id" name="client_id" required minlength="4" maxlength="8" size="12"/>
        </span>

        <span>
            <label for="battery_id">Batterie #</label>
            <input type="text" id="battery_id" name="battery_id" size="12"/>
        </span>
    </div>

    <div class="input-group">
        <!-- <span>
            <label for="cell_tech">Cell tech</label>

            <select id="cell_tech" name="cell_tech" bind:value={cell_tech}>
            {#each cell_tech_list as tech}
                <option value="{tech}">{tech}</option>
            {/each}
            </select>
        </span> -->

        <span>
            <label for="cells_s">Cellules Série</label>
            <input type="number" id="cells_s" name="cells_s" size="3"
                style="width: 50px;"
                min="1" max="16" bind:value={cells_s} on:input={updateParams} />
        </span>

        <span>
            <label for="cells_p">Cellules Parallèle</label>
            <input type="number" id="cells_p" name="cells_p" size="3"
            style="width: 50px;"
                min="1" bind:value={cells_p} on:input={updateParams} />
        </span>

        <span>
            <label for="cell_cap">Capacité cellule</label>
            <input type="number" id="cell_cap" name="cell_p" size="5"
                style="width: 70px;"
                min="1" step="100" bind:value={cell_cap} on:input={updateParams} />
        </span>
    </div>

</div>

<style>
    .container {
        background-color: #3aaa35;
        display: flex;
        /* justify-content: space-around; */
        justify-content: space-between;
        flex-wrap: wrap;
        padding: 16px;
    }
    span {
        margin-left: 10px;
        margin-right: 10px;
    }
    label {
        margin-right: 6px;
    }
</style>