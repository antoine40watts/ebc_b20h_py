<script>
    let cell_tech_list = [
        "Li-ion",
        "Li-Fe",
        "NiMH",
        "Lead Acid",
        "other",
    ]

    export let cell_tech = cell_tech_list[0];
    export let cells_s = 1;
    export let cells_p = 1;
    export let cell_cap = 2200;

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
            <label for="cells_s">Cells Series</label>
            <input type="number" id="cells_s" name="cells_s" size="2"
                bind:value={cells_s} />
        </span>

        <span>
            <label for="cells_p">Cells Parallel</label>
            <input type="number" id="cells_p" name="cells_p" size="2"
                bind:value={cells_p} />
        </span>

        <span>
            <label for="cell_cap">Cell Capacity</label>
            <input type="number" id="cell_cap" name="cell_p" size="5"
                bind:value={cell_cap} />
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